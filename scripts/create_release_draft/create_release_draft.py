import datetime
import requests
from requests.auth import HTTPBasicAuth
import hashlib
import json
import os.path
import sys

CONFIG = json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')))
VERSION_MAJOR = CONFIG['VERSION_MAJOR']
VERSION_MINOR = CONFIG['VERSION_MINOR']
VERSION_PATCH = CONFIG['VERSION_PATCH']
VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
GITHUB_USER = CONFIG['GITHUB_AUTH']['user']
GITHUB_KEY = CONFIG['GITHUB_AUTH']['key']


def sha256_checksum(filename, block_size=65536):
    """calculate the SHA256 checksum for a local file"""
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()


def create_github_release(path: str):
    """draft a release at GitHub"""

    release_text = """Release date: {date}
SHA-256: {header_hash} (json.hpp), {include_hash} (include.zip), {xz_hash} (json.tar.xz)

### Summary

### :boom: Breaking changes

### :sparkles: New Features

### :bug: Bug Fixes

### :zap: Improvements

### :hammer: Further Changes

### :fire: Deprecated functions

""".format(date=datetime.date.today().isoformat(),
           header_hash=sha256_checksum(os.path.join(path, 'release_files/json.hpp')),
           include_hash=sha256_checksum(os.path.join(path, 'release_files/include.zip')),
           xz_hash=sha256_checksum(os.path.join(path, 'release_files/json.tar.xz')))

    payload = {
        'tag_name': 'v{version}'.format(version=VERSION),
        'name': 'JSON for Modern C++ version {version}'.format(version=VERSION),
        'draft': True,
        'discussion_category_name': 'general',
        'body': release_text
    }

    r = requests.post(url='https://api.github.com/repos/nlohmann/json/releases',
                      auth=HTTPBasicAuth(GITHUB_USER, GITHUB_KEY),
                      json=payload)
    release = r.json()
    print(release)

    assets_url = release['assets_url']
    upload_url = assets_url.replace('api.github.com', 'uploads.github.com')

    files_to_upload = [
        {'name': 'json.hpp', 'Content-Type': 'application/octet-stream'},
        {'name': 'json.hpp.asc', 'Content-Type': 'application/octet-stream'},
        {'name': 'json_fwd.hpp', 'Content-Type': 'application/octet-stream'},
        {'name': 'json_fwd.hpp.asc', 'Content-Type': 'application/octet-stream'},
        {'name': 'include.zip', 'Content-Type': 'application/zip'},
        {'name': 'include.zip.asc', 'Content-Type': 'application/octet-stream'},
        {'name': 'json.tar.xz', 'Content-Type': 'application/x-xz'},
        {'name': 'json.tar.xz.asc', 'Content-Type': 'application/octet-stream'}
    ]

    for file in files_to_upload:
        params = {'name': file['name']}
        headers = {'Content-Type': file['Content-Type']}
        r = requests.post(url=upload_url,
                          auth=HTTPBasicAuth(GITHUB_USER, GITHUB_KEY),
                          params=params, headers=headers,
                          data=open(os.path.join(path, 'release_files/{filename}'.format(filename=file['name'])), 'rb'))
        print('uploaded file {filename} to github with code {status_code}'.format(filename=file['name'],
                                                                                  status_code=r.status_code))
        print(r.json())


if __name__ == '__main__':
    path = sys.argv[1]
    create_github_release(path)

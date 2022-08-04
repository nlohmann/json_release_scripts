# coding=utf-8

from typing import List, Optional
import requests
import re
import os.path
from PIL import Image
import glob
import json
import sys

CONFIG = json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')))
GITHUB_AUTH=(CONFIG['GITHUB_AUTH']['user'], CONFIG['GITHUB_AUTH']['key'])


def get_images_from_readme(path: Optional[str]) -> List[str]:
    github_user_re = re.compile(r'https://github.com/([a-zA-Z0-9-_\-]+)')

    if path is None:
        readme_file = requests.get('https://github.com/nlohmann/json/raw/develop/README.md').text
    else:
        readme_file = open(path).read()

    thanks_section = readme_file.split('I deeply appreciate the help of the following people')[1].split('Thanks a lot for helping out!')[0]

    url_scheme = 'https://api.github.com/users/{username}'

    usernames = set(github_user_re.findall(thanks_section))

    for username in usernames:
        print(username)

        if os.path.exists('cache/{username}'.format(username=username)):
            continue

        try:
            user_info = requests.get(url_scheme.format(username=username), auth=GITHUB_AUTH).json()
            image = requests.get(user_info['avatar_url']).content
            if len(image):
                with open('cache/{username}'.format(username=username), 'wb') as code:
                    code.write(image)
        except KeyError:
            pass

    return list(sorted(usernames))


def create_large_image():
    size = 64

    image_files = glob.glob('cache/*')
    result = Image.new("RGB", (4 * size, 79 * size))

    x_index = 0
    y_index = 0
    for image_idx, image_file in enumerate(image_files):
        img = Image.open(image_file)
        img.thumbnail((size, size), Image.ANTIALIAS)

        x_index += size
        if x_index == result.size[0]:
            x_index = 0
            y_index += size

        try:
            result.paste(img, (x_index, y_index, x_index + size, y_index + size))
        except Exception as e:
            print(image_file, e)

    result.save(os.path.expanduser('avatars.png'))


def get_contributors_images() -> List[str]:
    url = 'https://api.github.com/repos/nlohmann/json/contributors'

    page = 1
    usernames = []
    while True:
        res = requests.get(url=url, params={'page': page, 'per_page': 100}, auth=GITHUB_AUTH)
        if not res.ok:
            break

        contributors = res.json()

        if len(contributors) == 0:
            break

        page += 1

        for contributor in contributors:
            username = contributor['login']
            print(username)
            usernames.append(username)

            if os.path.exists(f'cache/{username}'):
                continue

            try:
                image = requests.get(contributor['avatar_url']).content
                if len(image):
                    with open(f'cache/{username}', 'wb') as code:
                        code.write(image)
            except KeyError:
                pass

    return sorted(usernames)


if __name__ == '__main__':
    usernames_readme = get_images_from_readme(path=sys.argv[1] if len(sys.argv) > 1 else None)
    usernames_all = get_contributors_images()

    # these accounts have not contributed via a merged PR (or are bots)
    non_contributors = ['cjh1', 'remyabel2', 'Francois-air', 'mstan-xx',
                        'dmenendez-gruposantander', 'palmer-dabbelt',
                        'intelmatt', 'mend-bolt-for-github[bot]', 'bradfora']

    found_missing_contributor = False
    for user in (set(usernames_all) - set(non_contributors)) - set(usernames_readme):
        print(f'⚠️ {user} is not in README')
        found_missing_contributor = True

    if found_missing_contributor:
        sys.exit(1)

    create_large_image()

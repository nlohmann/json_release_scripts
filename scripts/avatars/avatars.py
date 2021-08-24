# coding=utf-8

import requests
import re
import os.path
from PIL import Image
import glob
import json
import sys

CONFIG = json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')))
GITHUB_AUTH=(CONFIG['GITHUB_AUTH']['user'], CONFIG['GITHUB_AUTH']['key'])


def get_images_from_readme(path):
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


def create_large_image():
    size = 64

    image_files = glob.glob('cache/*')
    result = Image.new("RGB", (3 * size, 83 * size))

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


def get_contributors_images():
    url = 'https://api.github.com/repos/nlohmann/json/contributors?page={page}'
    pages = 3

    for page in range(1, pages+1):
        contributors = requests.get(url.format(page=page), auth=GITHUB_AUTH).json()
        for contributor in contributors:
            print(contributor['login'])

            if os.path.exists('cache/{username}'.format(username=contributor['login'])):
                continue

            try:
                image = requests.get(contributor['avatar_url']).content
                if len(image):
                    with open('cache/{username}'.format(username=contributor['login']), 'wb') as code:
                        code.write(image)
            except KeyError:
                pass


if __name__ == '__main__':
    get_images_from_readme(path=sys.argv[1] if len(sys.argv) > 1 else None)
    get_contributors_images()
    create_large_image()

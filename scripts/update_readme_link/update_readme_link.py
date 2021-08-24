import sys
import os
import os.path
import re
import subprocess
import codecs


def get_readme_link(path) -> str:
    """get the generated Wandbox URL (used to replace existing links in the README file later)"""
    content = open(os.path.join(path, 'doc/examples/README.link')).read()
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
    return urls[0]


if __name__ == '__main__':
    path = sys.argv[1]

    # get previous link
    #old_readme_link = get_readme_link(path)
    #print(f'old README link: {old_readme_link}')

    # delete links
    os.remove(os.path.join(path, 'doc/examples/README.link'))
    os.remove(os.path.join(path, 'doc/examples/README.output'))

    # regenerate link and output
    print('regenerate link for README example...')
    subprocess.check_output(['make', 'examples/README.output', 'examples/README.link', '-C', 'doc'], cwd=path)

    # get new link
    new_readme_link = get_readme_link(path)
    print(f'new README link: {new_readme_link}')

    # replace the link
    print('updating README.md')
    readme_content = codecs.open(os.path.join(path, 'README.md'), 'r', encoding='UTF-8').read()
    new_readme_content = re.sub(r'https://wandbox.org/permlink/[^)]+', new_readme_link, readme_content)
    codecs.open(os.path.join(path, 'README.md'), 'w', encoding='UTF-8').write(new_readme_content)

    print('adding files to git')
    subprocess.check_output(['git', 'add', 'README.md', 'doc/examples/README.output', 'doc/examples/README.link'], cwd=path)

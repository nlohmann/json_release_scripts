import sys
from typing import List, Optional
import json
import os.path
import os
import codecs
import glob
import re
import subprocess

CONFIG = json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')))
VERSION_MAJOR = CONFIG['VERSION_MAJOR']
VERSION_MINOR = CONFIG['VERSION_MINOR']
VERSION_PATCH = CONFIG['VERSION_PATCH']
VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"


def version_replace(filename: str, version_line_number: Optional[int], marker_string: str, version_string: str, regex=r'\d+\.\d+\.\d+'):
    """replace version entries by the new version"""
    print(f"patching {filename}")
    # read file
    content_lines = codecs.open(filename, 'r', encoding='UTF-8').readlines()

    # no line number given: find it with the marker string
    if version_line_number is None:
        for content_line_number, content_line in enumerate(content_lines):
            if marker_string in content_line:
                version_line_number = content_line_number
                break

    assert version_line_number is not None, 'no version line number given, and no line with marker string found'

    # the version should be in the n-th line
    version_line = content_lines[version_line_number]
    assert marker_string in version_line, 'marker string was not found in version line'

    # replace version
    new_version_line = re.sub(regex, version_string, version_line)
    assert version_string in new_version_line, 'replacement failed'

    # add new line to file
    new_file = content_lines[0:version_line_number] + [new_version_line] + content_lines[version_line_number + 1:]

    # write changed file
    codecs.open(filename, 'w', encoding='UTF-8').writelines(new_file)


def patch_release(path) -> List[str]:
    """bump the version numbers in the repository files"""

    os.chdir(path)

    patched_files = []

    ################
    # source files #
    ################

    files = glob.glob('*/nlohmann/json.hpp') + glob.glob('test/src/*.cpp', recursive=True)
    patched_files += files

    for file in files:
        version_replace(file, 3, 'version', VERSION)

    ###############
    # other files #
    ###############

    patched_files += ['CMakeLists.txt', 'doc/index.md', 'meson.build',
                      'wsjcpp.yml', '.github/ISSUE_TEMPLATE/Bug_report.md', 'CITATION.cff']

    version_replace('CMakeLists.txt', None, 'project(nlohmann_json', VERSION)
    version_replace('doc/index.md', None, '@version', VERSION)
    version_replace('meson.build', None, 'version', VERSION)
    version_replace('wsjcpp.yml', None, 'version: "v3', VERSION)
    version_replace('.github/ISSUE_TEMPLATE/Bug_report.md', None, 'latest release version', VERSION)
    version_replace('CITATION.cff', None, 'version: 3', VERSION)

    ##########################
    # meta() test and output #
    ##########################

    files = ['test/src/unit-meta.cpp', 'doc/examples/meta.output']
    patched_files += files

    for file in files:
        version_replace(file, None, '"string"', VERSION)
        version_replace(file, None, '"major"', VERSION_MAJOR, regex=r'\d+')
        version_replace(file, None, '"minor"', VERSION_MINOR, regex=r'\d+')
        version_replace(file, None, '"patch"', VERSION_PATCH, regex=r'\d+')

    ################
    # magic string #
    ################

    files = glob.glob('*/nlohmann/json.hpp')
    patched_files += files

    for file in files:
        version_replace(file, None, '961c151d2e87f2686a955a9be24d316f1362bf21', VERSION)
        version_replace(file, None, 'NLOHMANN_JSON_VERSION_MAJOR', VERSION_MAJOR, regex=r'\d+')
        version_replace(file, None, 'NLOHMANN_JSON_VERSION_MINOR', VERSION_MINOR, regex=r'\d+')
        version_replace(file, None, 'NLOHMANN_JSON_VERSION_PATCH', VERSION_PATCH, regex=r'\d+')

    return list(set(patched_files))


if __name__ == '__main__':
    path = sys.argv[1]
    patched_files = patch_release(path)

    for patched_file in patched_files:
        print(f'adding file {patched_file} to git')
        subprocess.check_output(['git', 'add', patched_file])

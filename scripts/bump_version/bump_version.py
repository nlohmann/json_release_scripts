import glob
import sys
from typing import List, Optional
import json
import os.path
import os
import codecs
import re
import subprocess

CONFIG = json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')))
VERSION_MAJOR = CONFIG['VERSION_MAJOR']
VERSION_MINOR = CONFIG['VERSION_MINOR']
VERSION_PATCH = CONFIG['VERSION_PATCH']
VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"


def version_replace(filename: str,
                    version_line_number: Optional[int],
                    marker_string: str,
                    version_string: str,
                    regex=r'\d+\.\d+\.\d+'):
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

    assert version_line_number is not None, f'{filename}: no version line number given, and no line with marker string "{marker_string}" found'

    # the version should be in the n-th line
    version_line = content_lines[version_line_number]
    assert marker_string in version_line, f'{filename}: marker string "{marker_string}" was not found in version line {version_line_number}'

    # replace version
    new_version_line = re.sub(regex, version_string, version_line)
    assert version_string in new_version_line, f'{filename}: replacement failed with marker string "{marker_string}"'

    # add new line to file
    new_file = content_lines[0:version_line_number] + [new_version_line] + content_lines[version_line_number + 1:]

    # write changed file
    codecs.open(filename, 'w', encoding='UTF-8').writelines(new_file)


def patch_release(path):
    """bump the version numbers in the repository files"""

    os.chdir(path)

    ###################
    # REUSE templates #
    ###################

    version_replace('.reuse/templates/json.jinja2', None, 'version', VERSION)
    version_replace('.reuse/templates/json_support.jinja2', None, 'version', VERSION)

    ###############
    # other files #
    ###############

    version_replace('CMakeLists.txt', None, 'project(nlohmann_json', VERSION)
    version_replace('meson.build', None, 'version', VERSION)
    version_replace('wsjcpp.yml', None, 'version: "v3', VERSION)
    version_replace('.github/ISSUE_TEMPLATE/bug.yaml', None, 'please enter the version number', VERSION)
    version_replace('CITATION.cff', None, 'version: 3', VERSION)
    version_replace('docs/examples/nlohmann_json_version.output', None, 'version', VERSION)

    ###############
    # meta() test #
    ###############

    version_replace('tests/src/unit-meta.cpp', None, '"string"', VERSION)
    version_replace('tests/src/unit-meta.cpp', None, '"major"', VERSION_MAJOR, regex=r'\d+')
    version_replace('tests/src/unit-meta.cpp', None, '"minor"', VERSION_MINOR, regex=r'\d+')
    version_replace('tests/src/unit-meta.cpp', None, '"patch"', VERSION_PATCH, regex=r'\d+')

    ################
    # magic string #
    ################

    version_replace('include/nlohmann/json.hpp', None, '961c151d2e87f2686a955a9be24d316f1362bf21', VERSION)

    ######################
    # version definition #
    ######################

    # definition of the version
    version_replace('include/nlohmann/detail/abi_macros.hpp', None, '#define NLOHMANN_JSON_VERSION_MAJOR', VERSION_MAJOR, regex=r'\d+')
    version_replace('include/nlohmann/detail/abi_macros.hpp', None, '#define NLOHMANN_JSON_VERSION_MINOR', VERSION_MINOR, regex=r'\d+')
    version_replace('include/nlohmann/detail/abi_macros.hpp', None, '#define NLOHMANN_JSON_VERSION_PATCH', VERSION_PATCH, regex=r'\d+')
    # version check
    version_replace('include/nlohmann/detail/abi_macros.hpp', None, '#if NLOHMANN_JSON_VERSION_MAJOR !=', f'#if NLOHMANN_JSON_VERSION_MAJOR != {VERSION_MAJOR} || NLOHMANN_JSON_VERSION_MINOR != {VERSION_MINOR} || NLOHMANN_JSON_VERSION_PATCH != {VERSION_PATCH}', regex=r'.+')


if __name__ == '__main__':
    path = sys.argv[1]

    # patch files
    patch_release(path)

    # call REUSE to patch copyright headers
    print('adding new copyright headers')
    subprocess.check_output(['make', 'reuse'], cwd=path)

    # create single-header file
    print('creating single-header file')
    os.remove(os.path.join(path, 'single_include/nlohmann/json.hpp'))
    subprocess.check_output(['make', 'amalgamate'], cwd=path)

    # remove output files
    print('removing example output files')
    for f in glob.glob(os.path.join(path, 'docs', 'examples', '*.output')):
        os.remove(f)

    # re-generate output
    print('re-generating example output files')
    # Xcode has issues with C++20 constructs, so we use Homebrew's GCC
    env = {'CXX': 'g++-11', 'PATH': '/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'}
    res = subprocess.check_output(['make', 'create_output', '-j16'], cwd=os.path.join(path, 'docs'), env=env)
    assert res, 're-generating example output files failed'

    # add changed files to git
    subprocess.check_output(['git', 'add', '-u'])

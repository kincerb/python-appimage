import argparse
import json
import re
import sys
from pathlib import Path

import requests


URI_BASE = 'https://api.github.com/repos/python/cpython/tags?per_page=100&page={0}'
CLEAN_REGEX = re.compile(r'^v?3\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)$') # Skip alpha, beta, release candidates, etc


# def _basedir_finder():
#     return Path(__file__).parent
# 
# 
# def get_data_file(minor_version, basedir_finder=_basedir_finder):
#     base = basedir_finder()
#     filename = 'version_list3.{0}.json'.format(minor_version)
#     return base.joinpath(filename)
# 
# 
# def read_data(data_file_path):
#     try:
#         with data_file_path.open() as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return []
# 
# 
# def write_data(data, data_file_path):
#     with data_file_path.open('w') as f:
#         json.dump(data, f)
# 

def get_versions(uri=URI_BASE):
    page = 1
    while True:
        data = requests.get(uri.format(page)).json()
#        print(data)
        if not data:
            break
        if page > 2:
            break
        for tag in data:
            yield tag.get('name')
        page += 1


def clean_versions(versions):
    for version in versions:
        match = CLEAN_REGEX.match(version)
        if match:
#            print(version)
            yield 3, int(match['minor']), int(match['patch'])


def filter_on_minor(versions, only_match):
    for version in versions:
        if version[1] == only_match:
            yield version


def parse_args():
    parser = argparse.ArgumentParser(description='Get the latest patch version of Python for a given minor version.')
    parser.add_argument('-v', dest='version', type=int, default=8, help='The minor version to look for. (default=8)')

    return parser.parse_args()


def main(minor_version):
#    data_file_path = get_data_file(minor_version=minor_version)
#    data = read_data(data_file_path)

    versions = clean_versions(get_versions())
    versions = sorted(filter_on_minor(versions, only_match=minor_version), reverse=True)
    versions = ['{0}.{1}.{2}'.format(*version) for version in versions]
    print(versions[0])
#    if (data and versions) and data != versions and versions[0] > data[0]:
#        write_data(versions, data_file_path)


if __name__ == "__main__":
    args = parse_args()
    main(args.version)

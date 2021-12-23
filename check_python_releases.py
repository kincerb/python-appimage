import argparse
import json
import logging
import logging.config
import re
import urllib
import urllib.parse
import urllib.request

URI_BASE = 'https://api.github.com/repos/python/cpython/tags'

CLEAN_REGEX = re.compile(r'^v?3\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)$')  # Skip alpha, beta, release candidates, etc


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

def get_versions(uri: str = URI_BASE, limit: int = 50):
    return


def _get_api_json(uri: str, per_page: int = 1, page: int = 1) -> json:
    params = urllib.parse.urlencode({'per_page': per_page, 'page': page})
    with urllib.request.urlopen(f'{uri}?{params}') as f:
        content = f.read().decode()
    return json.loads(content)


def clean_versions(versions):
    for version in versions:
        match = CLEAN_REGEX.match(version)
        if match:
            yield 3, int(match['minor']), int(match['patch'])


def filter_on_minor(versions, only_match):
    for version in versions:
        if version[1] == only_match:
            yield version


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Get the latest patch version of Python for a given minor version.')
    parser.add_argument('-v', dest='version', type=int, default=8, help='The minor version to look for. (default=8)')

    return parser.parse_args()


def configure_logging(verbosity: int = 0) -> None:
    """Configure logging.

    Keyword Arguments:
        verbosity (int):
            Integer representing level of verbosity
            Default: 0

    Returns:
        None
    """
    level = 'INFO' if verbosity == 0 else 'DEBUG'
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'console': {
                'format': '%(levelname)-8s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'console',
            }
        },
        'loggers': {
            'root': {
                'level': level,
                'handlers': ['console'],
                'propagate': False
            }
        }
    }
    logging.config.dictConfig(config)


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

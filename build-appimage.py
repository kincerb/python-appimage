#!/usr/bin/env python3
import argparse
import logging
import logging.config
import logging.handlers


def main():
    args = get_args()
    configure_logging(verbosity=args.verbosity)


def get_args():
    """Parse arguments passed at invocation.

    Returns:
        argparse.Namespace: Parsed argument namespace.
    """
    parser = argparse.ArgumentParser(
        description='Git credential helper',
        epilog='Example: %(prog)s get'
    )
    parser.add_argument('operation',
                        action='store',
                        type=str,
                        help='Git action (get|store|erase)')
    parser.add_argument('-u', '--url',
                        required=True,
                        dest='url',
                        action='store',
                        help='Repo base url')
    parser.add_argument('-v', '--verbose',
                        required=False,
                        dest='verbosity',
                        action='count',
                        default=0,
                        help='Increase output verbosity.')
    return parser.parse_args()


def configure_logging(verbosity=0):
    """Configures logging in the globally defined logging object.

    Args:
        verbosity (int, optional): Increment to increase verbosity.
        Defaults to 0.

    Returns:
        None
    """
    level = 'INFO' if verbosity == 0 else 'DEBUG'
    config = {
        'version': 1,
        'disable_existing_loggings': False,
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
            __name__: {
                'level': level,
                'handlers': ['console'],
                'propagate': False
            }
        }
    }
    logging.config.dictConfig(config)


if __name__ == '__main__':
    main()

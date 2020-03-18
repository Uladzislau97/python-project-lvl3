#!/usr/bin/env python3
import os
import logging

import argparse

from page_loader import load_page


LOGGING_LEVEL_NAMES = (
    NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
) = (
    'notset', 'debug', 'info', 'warning', 'error', 'critical'
)


logging_levels = {
    NOTSET: logging.NOTSET,
    DEBUG: logging.DEBUG,
    INFO: logging.INFO,
    WARNING: logging.WARNING,
    ERROR: logging.ERROR,
    CRITICAL: logging.CRITICAL
}


def logging_level(level_name):
    try:
        return logging_levels[level_name]
    except ValueError:
        raise argparse.ArgumentTypeError(
            'Unknown logging level: "{}". Use one of this: {}'.format(
                level_name,
                ', '.join(LOGGING_LEVEL_NAMES),
            )
        )


def main():
    parser = argparse.ArgumentParser(
        description=(
            'Downloads the internet page and put it in the specified folder.'
        )
    )
    parser.add_argument('address')
    parser.add_argument(
        '-o', '--output',
        help='set output path',
        type=str,
        default=os.getcwd()
    )
    parser.add_argument(
        '-l', '--logging',
        help='set logging level',
        type=logging_level,
        default=WARNING
    )
    args = parser.parse_args()
    load_page(args.address, args.output, args.logging)


if __name__ == "__main__":
    main()

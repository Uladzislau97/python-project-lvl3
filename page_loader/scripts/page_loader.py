#!/usr/bin/env python3
import os

import argparse

from page_loader import load_page


def main():
    parser = argparse.ArgumentParser(
        description='Downloads the internet page and put it in the specified folder.'
    )
    parser.add_argument('address')
    parser.add_argument(
        '-o', '--output',
        help='set output path',
        type=str,
        default=os.getcwd()
    )
    args = parser.parse_args()
    load_page(args.address, args.output)


if __name__ == "__main__":
    main()

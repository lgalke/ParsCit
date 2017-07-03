# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# Parsing of command-line arguments
# https://docs.python.org/3/howto/argparse.html
import argparse
# Subprocess management, such as invoking ParsCit
# https://docs.python.org/3/library/subprocess.html
import subprocess
"""
Example usage:
python3 citex.py -h
python3 citex.py file1.txt file2.txt file3.txt
"""


def process_file(path):
    print("Processing", path)
    # ...TODO


def main():
    print("[citex] Hello world")

    # argument parser setup
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'paths',  # the identifier
        nargs='+',  # at least one but arbitrary amount of files
        help='Specify the files to extract citations from.')

    # invoke actual parsing of command line arguments
    args = parser.parse_args()

    for path in args.paths:  # Loop over all provided paths...
        process_file(path)  # ...and process each file.


if __name__ == '__main__':
    main()

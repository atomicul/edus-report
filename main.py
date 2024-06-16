#!/usr/bin/env python3

import sys
import argparse
import textwrap

from app import App


def main():
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description="CLI tool to exctract data from the edus.ro platform.",
        epilog=textwrap.dedent("""
                Environment variables:
                  USERNAME      email or phone number used for auth
                  PASSWORD      password to be used for auth
                  AUTH_COOKIE   'catalogsessionid' cookie on the website
                In order to skip the authentication prompt, provide either the `AUTH_COOKIE` or the both of `USERNAME` and `PASSWORD`
            """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-s",
        "--student",
        help="a substring to be searched in the student name, in the case of a parent account",
    )

    parser.add_argument(
        "-a",
        "--action",
        choices=["aggregates", "absences", "grades", "report"],
        help="lookup action to perform on the student",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["csv", "txt"],
        default="txt",
        help="the format of the result table",
    )

    parser.add_argument("-o", "--output", help="file to write the result table in")

    parser.add_argument(
        "--shush",
        action="store_true",
        help="turn off all non mandatory logging to stdout",
    )

    App(parser.parse_args()).run()


if __name__ == "__main__":
    main()

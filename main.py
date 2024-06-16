#!/usr/bin/env python3

import os
import argparse
import textwrap

from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from prettytable import PrettyTable

from getpass import getpass

from scraper import (
    authenticate_by_session_id,
    authenticate_by_credentials,
    ParentEdusScraper,
)
from scraper.base_edus_scraper import BaseEdusScraper


def main():
    parser = argparse.ArgumentParser(
        prog="edus-report",
        description="CLI tool to exctract data from the edus.ro platform.",
        epilog=textwrap.dedent("""
            Environment variables:
                USERNAME      email or phone number used for auth
                PASSWORD      password to be used for auth
                AUTH_COOKIE   'catalogsessionid' cookie on the webside
            In order to skip the authentication prompt, provide either the `AUTH_COOKIE` or the both of `USERNAME` and `PASSWORD`
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--shush",
        action="store_true",
        help="turn off all non mandatory logging to stdout",
    )
    parser.add_argument(
        "-s",
        "--student",
        help="a substring to be searched in the student name, in the case of a parent account",
    )
    parser.add_argument(
        "-a",
        "--action",
        choices=["aggregates"],
        help="lookup action to perform on the student",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["csv", "txt"],
        default="txt",
        help="the format of the result table",
    )
    args = parser.parse_args()

    opts = Options()
    opts.add_argument("--headless")
    driver = webdriver.Chrome(opts)

    if "AUTH_COOKIE" in os.environ:
        scraper = authenticate_by_session_id(driver, os.environ["AUTH_COOKIE"])
    elif "USERNAME" in os.environ and "PASSWORD" in os.environ:
        scraper = authenticate_by_credentials(
            driver, os.environ["USERNAME"], os.environ["PASSWORD"]
        )
    else:
        match options_select(
            ["Authenticate by credentials", "Authenticate by session cookie"]
        ):
            case 0:
                username = input("username: ")
                password = getpass("password: ")
                scraper = authenticate_by_credentials(driver, username, password)
            case 1:
                session_cookie = input("session cookie: ")
                scraper = authenticate_by_session_id(driver, session_cookie)
            case _:
                raise ValueError

    if not args.shush:
        print(f"Logged in as {scraper.account_name}")

    if isinstance(scraper, ParentEdusScraper):
        if args.student:
            selection = [
                x for x in scraper.students if args.student.lower() in x.name.lower()
            ]
        else:
            selection = scraper.students

        match len(selection):
            case 0:
                raise ValueError("No student matches the criteria")
            case 1:
                selection[0].set_as_active()
            case _:
                print("Select a student:")
                i = options_select([s.name for s in selection])
                scraper.students[i].set_as_active()

        if not args.shush:
            assert scraper.active_student is not None
            print(f"Selected {scraper.active_student.name} for inspection")

    actions = [("aggregates", "Show aggregate values. (sums, means)", aggregates)]

    if args.action:
        try:
            fn = next(filter(lambda x: x[0] == args.action, actions))[2]
        except StopIteration:
            raise ValueError("Unexpected action given")
    else:
        i = options_select([x[1] for x in actions])
        fn = actions[i][2]

    def print_loading(x):
        if not args.shush:
            print(f"Loading {int(x*100)}%")

    table = fn(scraper, print_loading)

    match args.format:
        case "csv":
            print(*(",".join(map(str, row)) for row in table), sep="\n")
        case "txt":
            tl = PrettyTable(table[0])
            tl.add_rows(table[1:])
            print(tl)


def aggregates(scraper: BaseEdusScraper, progress) -> List[List[str]]:
    absences = scraper.get_absences(progress=progress)
    head = ["total absences", "unmotivated absences", "grade average"]
    body = []
    body.append(len(absences))
    body.append(sum(1 for a in absences if not a.is_motivated))

    grades = scraper.get_grades_by_subject(progress=progress)
    averages = [round(sum(x.grade for x in x) / len(x)) for x in grades.values()]
    year_wide_average = round(sum(averages) / len(averages), 2)
    body.append(year_wide_average)

    return [head, body]


def options_select(options: List[str]):
    print(*(f"{i}) {var}" for i, var in enumerate(options, 1)), sep="\n")
    print()

    while True:
        try:
            i = int(input(f"Pick an option [1-{len(options)}]: "))
            if i not in range(1, len(options) + 1):
                raise ValueError
            return i - 1
        except Exception:
            pass


if __name__ == "__main__":
    main()

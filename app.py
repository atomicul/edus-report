import functools
import os
import argparse

import sys
from typing import Iterator, List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from prettytable import PrettyTable

from getpass import getpass

from selenium.webdriver.chrome.webdriver import WebDriver

from scraper import (
    authenticate_by_session_id,
    authenticate_by_credentials,
    ParentEdusScraper,
)

from io_utils import options_select, question

import actions as ac
from scraper.base_edus_scraper import BaseEdusScraper


class App:
    ACTIONS = [
        ("aggregates", "Show aggregate values. (totals, year average)", ac.aggregates),
        ("absences", "Show all absences, most recent first", ac.absences),
        ("grades", "Show all grades, most recent first", ac.grades),
        ("report", "Show a per subject report", ac.per_subject_report),
    ]

    _args: argparse.Namespace

    def __init__(self, args: argparse.Namespace) -> None:
        self._args = args

    def run(self):
        opts = Options()
        opts.add_argument("--headless")
        driver = webdriver.Chrome(opts)

        scraper = self._auth_user(driver)

        self._select_student(scraper)

        # load_data
        _ = scraper.get_data(progress=self._print_loading)

        for table in self._perform_actions(scraper):
            self._print_table(table)

    def _auth_user(self, driver: WebDriver):
        if "AUTH_COOKIE" in os.environ:
            scraper = authenticate_by_session_id(driver, os.environ["AUTH_COOKIE"])
        elif "USERNAME" in os.environ and "PASSWORD" in os.environ:
            scraper = authenticate_by_credentials(
                driver, os.environ["USERNAME"], os.environ["PASSWORD"]
            )
        else:
            match options_select(
                list(
                    enumerate(
                        [
                            "Authenticate by credentials",
                            "Authenticate by session cookie",
                        ]
                    )
                ),
                key=lambda x: x[1],
            )[0]:
                case 0:
                    username = input("username: ")
                    password = getpass("password: ")
                    scraper = authenticate_by_credentials(driver, username, password)
                case 1:
                    session_cookie = input("session cookie: ")
                    scraper = authenticate_by_session_id(driver, session_cookie)
                case _:
                    raise ValueError

        if not self._args.shush:
            print(f"Logged in as {scraper.account_name}")

        return scraper

    def _select_student(self, scraper):
        if not isinstance(scraper, ParentEdusScraper):
            return

        if self._args.student:
            selection = [
                x
                for x in scraper.students
                if self._args.student.lower() in x.name.lower()
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
                options_select(selection, key=lambda x: x.name).set_as_active()

        if not self._args.shush:
            assert scraper.active_student is not None
            print(f"Selected {scraper.active_student.name} for inspection")

    def _perform_actions(self, scraper: BaseEdusScraper) -> Iterator[List[List[str]]]:
        if self._args.action:
            try:
                fn = next(filter(lambda x: x[0] == self._args.action, App.ACTIONS))[2]
            except StopIteration:
                raise ValueError("Unexpected action given")
        else:
            fn = options_select(App.ACTIONS, key=lambda x: x[1])[2]

        yield fn(scraper)

        if not self._args.shush and self._args.action is None:
            ans = question("Do you want to perform another action?", default=True)
            if ans:
                yield from self._perform_actions(scraper)

    def _print_table(self, table: List[List[str]]):
        write_to = open(self._args.output, "w") if self._args.output else sys.stdout
        write = functools.partial(print, file=write_to)
        match self._args.format:
            case "csv":
                write(*(",".join(map(str, row)) for row in table), sep="\n")
            case "txt":
                tl = PrettyTable(table[0])
                tl.add_rows(table[1:])
                write(tl)

    def _print_loading(self, x):
        if not self._args.shush:
            print(f"Loading {int(x*100)}%")

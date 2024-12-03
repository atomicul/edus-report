import re
import time
import functools
from datetime import date
import itertools
from typing import Dict, List, Callable, Optional, Tuple
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from .data import Grade, Absence


class BaseEdusScraper:
    WEBSITE_URL = "https://app.edus.ro"
    WAIT = 5

    _driver: WebDriver
    _wait: WebDriverWait
    _absences: Optional[List[Absence]] = None
    _grades: Optional[List[Grade]] = None

    def __init__(self, driver: WebDriver):
        self._driver = driver

        self._driver.set_window_size(1920, 1080)

        self._driver.implicitly_wait(BaseEdusScraper.WAIT)
        self._wait = WebDriverWait(self._driver, BaseEdusScraper.WAIT)

        self._driver.get(BaseEdusScraper.WEBSITE_URL)

    @property
    def student_dashboard(self) -> str:
        raise NotImplementedError("Not implemented on base class")

    @property
    @functools.cache
    def account_name(self):
        return (
            self._driver.find_element(
                By.XPATH, "(//nav[contains(@id, 'user-menu')]//span)[last()]"
            )
            .text.split("\n")[0]
            .strip()
        )

    def get_year_wide_average(
        self, *, progress: Callable[[float], None] = lambda _: None
    ) -> float:
        grades = self.get_grades_by_subject(progress=progress)
        averages = [round(sum(x.grade for x in x) / len(x)) for x in grades.values()]
        return round(sum(averages) / len(averages), 2)

    def get_absences(
        self, *, progress: Callable[[float], None] = lambda _: None
    ) -> List[Absence]:
        return self.get_data(progress=progress)[0]

    def get_absences_by_subject(
        self, *, progress: Callable[[float], None] = lambda _: None
    ):
        return BaseEdusScraper._group_by_subject(self.get_absences(progress=progress))

    def get_grades(
        self, *, progress: Callable[[float], None] = lambda _: None
    ) -> List[Grade]:
        return self.get_data(progress=progress)[1]

    def get_grades_by_subject(
        self, *, progress: Callable[[float], None] = lambda _: None
    ):
        return BaseEdusScraper._group_by_subject(self.get_grades(progress=progress))

    @staticmethod
    def _group_by_subject[T](x: List[T]) -> Dict[str, List[T]]:
        x_sorted = sorted(x, key=lambda x: x.subject)
        return dict(
            (k, list(g))
            for k, g in itertools.groupby(x_sorted, key=lambda x: x.subject)
        )

    def get_data(
        self, *, progress: Callable[[float], None] = lambda _: None
    ) -> Tuple[List[Absence], List[Grade]]:
        if self._absences is not None and self._grades is not None:
            return self._absences, self._grades

        progress(0)
        self._driver.get(self.student_dashboard)

        page_subtitle = self._driver.find_element(
            By.XPATH, "//div[contains(@class, 'page-subtitle')]"
        ).text
        school_year = [
            int(word)
            for word in page_subtitle.split()
            if re.search("^20[0-9][0-9]$", word)
        ][-1]

        subjects = self._driver.find_elements(
            By.XPATH, "//select[contains(@class, 'course-select')]/option"
        )
        subjects = [s.text for s in subjects]
        subjects = [s for s in subjects if "toate" not in s.lower()]

        absences: List[Absence] = []
        grades: List[Grade] = []

        for i, subject in enumerate(subjects, 1):
            self._driver.find_element(
                By.XPATH, "//span[contains(@class, 'select2')]"
            ).click()
            self._driver.find_element(By.XPATH, f"//li[text()='{subject}']").click()

            time.sleep(0.1)
            self._wait.until(
                lambda driver: "d-none"
                in driver.find_element(
                    By.XPATH, "//div[contains(@class, 'preloader-wrapper')]"
                ).get_attribute("class")
            )

            self._driver.implicitly_wait(0)

            def parse_date(x: str):
                day, month = map(int, x.split("."))
                d = date(school_year, month, day)
                if date.today() < d:
                    d = date(d.year - 1, d.month, d.day)
                return d

            def is_not_deleted(x: WebElement):
                return "deleted" not in str(x.get_attribute("class"))

            absence_elements = self._driver.find_elements(
                By.XPATH, "//span[contains(@class, 'student-missing')]"
            )
            absence_elements = filter(is_not_deleted, absence_elements)
            absences += [
                Absence(
                    subject,
                    parse_date(m.text),
                    "success" in str(m.get_attribute("class")),
                )
                for m in absence_elements
            ]

            grades_elements = self._driver.find_elements(
                By.XPATH, "//span[contains(@class, 'student-grade')]"
            )
            grades_elements = filter(is_not_deleted, grades_elements)
            grades_elements = (el.text.split("/") for el in grades_elements)
            grades += [
                Grade(subject, parse_date(d), int(grade))
                for grade, d in grades_elements
            ]

            self._driver.implicitly_wait(BaseEdusScraper.WAIT)

            progress(i / len(subjects))

        self._grades, self._absences = grades, absences

        return self._absences, self._grades

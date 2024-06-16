import functools
from datetime import date
import itertools
from typing import Dict, List, Callable, Optional, Tuple, Any
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
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
        return self._driver.find_element(
            By.XPATH, "//div[contains(@class, 'user-details')]/div"
        ).text

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
        school_year = int(page_subtitle.split()[-1])

        subjects = self._driver.find_elements(
            By.XPATH, "//select[contains(@class, 'course-select')]/option"
        )
        subjects = [s.text for s in subjects]

        absences: List[Absence] = []
        grades: List[Grade] = []

        for i, subject in enumerate(subjects, 1):
            self._driver.find_element(
                By.XPATH, "//span[contains(@class, 'select2')]"
            ).click()
            self._driver.find_element(By.XPATH, f"//li[text()='{subject}']").click()

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

            absence_elements = self._driver.find_elements(
                By.XPATH, "//span[contains(@class, 'student-missing')]"
            )
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
            grades_elements = (el.text.split("/") for el in grades_elements)
            grades += [
                Grade(subject, parse_date(d), int(grade))
                for grade, d in grades_elements
            ]

            self._driver.implicitly_wait(BaseEdusScraper.WAIT)

            progress(i / len(subjects))

        self._grades, self._absences = grades, absences

        return self._absences, self._grades

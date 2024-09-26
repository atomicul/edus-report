import functools
import itertools

from typing import Optional

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from . import BaseEdusScraper


class ParentEdusScraper(BaseEdusScraper):
    _active_student: Optional["Student"] = None

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    @property
    @functools.cache
    def students(self):
        student_item_selector = "//img[contains(@src, 'icons/student')]/.."

        name_elements = self._driver.find_elements(By.XPATH, student_item_selector)
        names = (el.text for el in name_elements)
        names = (name.strip() for name in names)

        link_elements = self._driver.find_elements(
            By.XPATH,
            f"{student_item_selector}/..//a[contains(@href, 'situatie-scolara')]",
        )
        links = (str(el.get_property("href")) for el in link_elements)

        students = itertools.zip_longest(names, links)
        students = [Student(self, name, link) for name, link in students]

        return students

    @property
    def active_student(self) -> Optional["Student"]:
        return self._active_student

    @property
    def student_dashboard(self):
        if self.active_student is None:
            raise ValueError("No selected student")
        return self.active_student.dashboard_link


class Student:
    _parent: "ParentEdusScraper"

    def __init__(self, parent: "ParentEdusScraper", name: str, link: str):
        self._parent = parent
        self._name = name
        self._link = link

    def __eq__(self, value, /) -> bool:
        if not isinstance(value, Student):
            return False
        return self.name == value.name and self.dashboard_link == value.dashboard_link

    @property
    def name(self):
        return self._name

    @property
    def dashboard_link(self):
        return self._link

    def set_as_active(self):
        self._parent._active_student = self

import re

from .base_edus_scraper import BaseEdusScraper
from .parent_edus_scraper import ParentEdusScraper
from .student_edus_scraper import StudentEdusScraper
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By


def authenticate_by_session_id(driver: WebDriver, session_token: str):
    driver.get(BaseEdusScraper.WEBSITE_URL)

    driver.add_cookie(
        {
            "name": "CATALOG_AUTH_TIME",
            "value": "1",
            "path": "/",
        }
    )

    driver.add_cookie(
        {
            "name": "catalogsessionid",
            "value": session_token,
            "path": "/",
        }
    )

    return _verify_authentication(driver)


def authenticate_by_credentials(driver: WebDriver, username: str, password: str):
    driver.get(
        BaseEdusScraper.WEBSITE_URL + "/cont/login",
    )

    driver.find_element(By.XPATH, "//form//input[@name='username']").send_keys(username)
    driver.find_element(By.XPATH, "//form//input[@name='password']").send_keys(password)

    driver.find_element(By.XPATH, "//form//input[@type='submit']").click()

    return _verify_authentication(driver)


def _verify_authentication(driver: WebDriver):
    driver.get(BaseEdusScraper.WEBSITE_URL)

    section = re.search(r"https?:\/\/[^\/]+\/([^\/]+)", driver.current_url)
    section = section and section.group(1)

    match section:
        case "parinte":
            return ParentEdusScraper(driver)
        case "elev":
            return StudentEdusScraper(driver)
        case _:
            raise ValueError("Authentication failed")

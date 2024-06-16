from selenium.webdriver.chrome.webdriver import WebDriver

from . import BaseEdusScraper


class StudentEdusScraper(BaseEdusScraper):
    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    @property
    def student_dashboard(self):
        return BaseEdusScraper.WEBSITE_URL + "/elev/situatie-scolara"

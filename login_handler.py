from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from config import BASE_URL


class LoginManager:
    LOGIN_URL = f"{BASE_URL}/logon.asp"

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def login(self, page):
        try:
            page.goto(self.LOGIN_URL)
            page.fill("#adminuser", self.username)
            page.fill("#adminPass", self.password)
            page.click("#btn1")
            
            try:
                page.wait_for_selector('td[align="center"][style="background-color:#eeeeee"]:has-text("© Copyright 2024 - Restoconcept")', timeout=5000)
                return True
            except PlaywrightTimeoutError:
                return False
        except Exception as e:
            return False

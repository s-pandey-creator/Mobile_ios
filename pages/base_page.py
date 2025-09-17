# pages/base_page.py
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class BasePage:
    def __init__(self, driver, default_timeout: int = 8):
        self.driver = driver
        self.default_timeout = default_timeout

    def find(self, by, locator, timeout=None):
        timeout = timeout if timeout is not None else self.default_timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )

    def find_all(self, by, locator, timeout=1):
        # quick poll to return list (may be empty)
        end = time.time() + timeout
        while time.time() < end:
            elems = self.driver.find_elements(by, locator)
            if elems:
                return elems
            time.sleep(0.15)
        return []

    def exists(self, by, locator, timeout=2):
        try:
            self.find(by, locator, timeout=timeout)
            return True
        except Exception:
            return False

    def safe_click(self, el):
        try:
            el.click()
            return True
        except Exception:
            try:
                # mobile tap fallback
                self.driver.execute_script("mobile: tap", {"element": el.id})
                return True
            except Exception:
                try:
                    loc = el.location
                    size = el.size
                    self.driver.execute_script("mobile: tap", {
                        "x": int(loc["x"] + size["width"] / 2),
                        "y": int(loc["y"] + size["height"] / 2)
                    })
                    return True
                except Exception:
                    return False

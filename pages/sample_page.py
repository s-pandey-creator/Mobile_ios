# pages/sample_page.py
import os
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SamplePage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout

    def wait_for_app(self):
        """Wait for main sample app UI to appear (safe, tolerant)."""
        # try a few common indicators used by the sample app
        candidates = [
            (AppiumBy.ACCESSIBILITY_ID, "test-Page"),
            (AppiumBy.ACCESSIBILITY_ID, "test-Title"),
            (AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeStaticText' AND label CONTAINS 'Welcome'"),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.TextView")')
        ]
        for by, val in candidates:
            try:
                WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((by, val))
                )
                return True
            except Exception:
                continue
        # fallback: at least wait for any static text element
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((AppiumBy.XPATH, "//XCUIElementTypeStaticText | //android.widget.TextView"))
            )
            return True
        except Exception:
            return False

    def open_ui_elements(self):
        """Navigate to UI Elements sample - best-effort."""
        try:
            btn = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-UI Elements")
            btn.click()
            return True
        except Exception:
            try:
                btn = self.driver.find_element(AppiumBy.XPATH, "//*[contains(translate(@label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'ui elements') or contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'ui elements')]")
                btn.click()
                return True
            except Exception:
                return False

    def get_text_from_button(self):
        """Example helper to return text shown on pressing a text button."""
        try:
            btn = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Text Button")
            btn.click()
            # wait for label to update
            el = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "test-Text"))
            )
            return (el.text or el.get_attribute("label") or el.get_attribute("value") or "").strip()
        except Exception:
            return ""

    def open_alert_and_close(self):
        """Open an alert and close it (best-effort)."""
        try:
            btn = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Alert")
            btn.click()
            # wait for alert
            try:
                alert_ok = WebDriverWait(self.driver, 6).until(
                    EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "OK"))
                )
                alert_ok.click()
                return True
            except Exception:
                # try generic alert close
                try:
                    ok = self.driver.find_element(AppiumBy.XPATH, "//*[contains(translate(@label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'ok') or contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'ok')]")
                    ok.click()
                    return True
                except Exception:
                    return False
        except Exception:
            return False

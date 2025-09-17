# tests/test_ui_elements.py
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from pages.sample_page import SamplePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.smoke
def test_open_ui_elements(driver):
    sp = SamplePage(driver)
    sp.wait_for_app()
    sp.open_ui_elements()

    # wait for 'Text Button' to be present using AppiumBy
    wait = WebDriverWait(driver, 15)
    el = wait.until(EC.presence_of_element_located((AppiumBy.NAME, "Text Button")))
    assert el is not None

def test_text_button_shows_text(driver):
    sp = SamplePage(driver)
    sp.wait_for_app()
    sp.open_ui_elements()
    sp.tap_text_button()
    text = sp.get_static_text()
    assert text and text.strip() != "", f"Expected static text after pressing Text Button, got: '{text}'"

def test_alert_opens_and_closes(driver):
    sp = SamplePage(driver)
    sp.wait_for_app()
    sp.open_ui_elements()
    sp.tap_alert()
    assert sp.is_alert_present(), "Expected alert to appear after tapping Alert"
    sp.close_alert_ok()
    # ensure Text Button visible again
    wait = WebDriverWait(sp.driver, 10)
    wait.until(EC.presence_of_element_located((AppiumBy.NAME, "Text Button")))

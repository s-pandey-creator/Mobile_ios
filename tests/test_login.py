# tests/test_login.py
import pytest
from pages.login_page import LoginPage
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Valid test account for Swag Labs
VALID_USER = "standard_user"
VALID_PASS = "secret_sauce"

def test_valid_login(driver):
    """User can log in with valid credentials."""
    lp = LoginPage(driver)
    lp.login(VALID_USER, VALID_PASS)

    # Verify post-login page contains "Products"
    wait = WebDriverWait(driver, 10)
    products_title = wait.until(
        EC.presence_of_element_located((AppiumBy.IOS_PREDICATE, 'label == "PRODUCTS"'))
    )
    assert products_title is not None, "Products page not visible after login"

def test_invalid_login_shows_error(driver):
    """Invalid login should display an error message."""
    lp = LoginPage(driver)
    lp.login("invalid_user", "wrong_password")
    error_text = lp.get_error_text()
    assert error_text.strip() != "", "Expected an error message for invalid login"

def test_logout(driver):
    """User can log out after logging in."""
    lp = LoginPage(driver)
    lp.login(VALID_USER, VALID_PASS)

    # open menu (hamburger icon usually on top-left)
    menu_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "test-Menu"))
    )
    menu_btn.click()

    # tap logout
    logout_btn = lp._find_first(lp.logout_btn_candidates)
    logout_btn.click()

    # Verify we see login screen again
    username_field = lp._find_first(lp.username_candidates)
    assert username_field is not None, "Username field not visible after logout"

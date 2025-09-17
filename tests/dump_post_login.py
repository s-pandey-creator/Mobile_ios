# tests/dump_post_login.py
import os
import time
from appium import webdriver
from appium.options.common import AppiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Read env vars
USERNAME = os.environ.get("BROWSERSTACK_USERNAME")
ACCESS_KEY = os.environ.get("BROWSERSTACK_ACCESS_KEY")
APP_ID = os.environ.get("APP_ID") or os.environ.get("BROWSERSTACK_APP")
DEVICE = os.environ.get("DEVICE", "iPhone 14")
OS_VERSION = os.environ.get("OS_VERSION", "18")

if not USERNAME or not ACCESS_KEY or not APP_ID:
    raise SystemExit("Set BROWSERSTACK_USERNAME, BROWSERSTACK_ACCESS_KEY and APP_ID in env before running")

caps = {
    "bstack:options": {
        "userName": USERNAME,
        "accessKey": ACCESS_KEY,
        "deviceName": DEVICE,
        "osVersion": OS_VERSION,
        "appiumVersion": "2.0.0",
        "projectName": "Mobile-Automation",
        "buildName": "post-login-dump",
        "sessionName": "dump-post-login"
    },
    "app": APP_ID,
    "automationName": "XCUITest"
}

options = AppiumOptions()
options.load_capabilities(caps)

hub = "https://hub-cloud.browserstack.com/wd/hub"
driver = webdriver.Remote(command_executor=hub, options=options)

try:
    wait = WebDriverWait(driver, 20)

    # Login with Swag Labs known credentials
    username = wait.until(EC.presence_of_element_located((By.NAME, "test-Username")))
    username.clear()
    username.send_keys("standard_user")

    password = driver.find_element(By.NAME, "test-Password")
    password.clear()
    password.send_keys("secret_sauce")

    driver.find_element(By.NAME, "test-LOGIN").click()

    # Wait for PRODUCTS screen
    try:
        wait.until(EC.presence_of_element_located((By.IOS_PREDICATE, 'label == "PRODUCTS"')))
    except Exception:
        wait.until(EC.presence_of_element_located((By.NAME, "test-ALL ITEMS")))

    time.sleep(1)  # small pause

    # Save page source + screenshot
    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/pagesource_post_login.xml", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.save_screenshot("artifacts/screenshot_post_login.png")

    print("✅ Saved post-login page source -> artifacts/pagesource_post_login.xml")
    print("✅ Saved post-login screenshot -> artifacts/screenshot_post_login.png")

finally:
    driver.quit()

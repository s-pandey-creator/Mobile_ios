# tests/check_locators.py
import os, json, time
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy

USERNAME = os.environ.get("BROWSERSTACK_USERNAME")
ACCESS_KEY = os.environ.get("BROWSERSTACK_ACCESS_KEY")
APP_ID = os.environ.get("APP_ID")
if not USERNAME or not ACCESS_KEY or not APP_ID:
    raise SystemExit("Set BROWSERSTACK_USERNAME, BROWSERSTACK_ACCESS_KEY and APP_ID environment variables first")

caps = {
    "bstack:options": {
        "userName": USERNAME,
        "accessKey": ACCESS_KEY,
        "deviceName": os.environ.get("DEVICE", "iPhone 14"),
        "osVersion": os.environ.get("OS_VERSION", "18"),
        "appiumVersion": "2.0.0"
    },
    "app": APP_ID,
    "automationName": "XCUITest",
}

print("Starting session to check locators...")
options = AppiumOptions()
options.load_capabilities(caps)
hub = "https://hub-cloud.browserstack.com/wd/hub"
driver = webdriver.Remote(command_executor=hub, options=options)

time.sleep(2)  # let app settle

candidates = [
    ("Sample iOS",           (AppiumBy.NAME, "Sample iOS")),
    ("UI Elements",          (AppiumBy.NAME, "UI Elements")),
    ("Text Button",          (AppiumBy.NAME, "Text Button")),
    ("Text",                 (AppiumBy.NAME, "Text")),
    ("Alert",                (AppiumBy.NAME, "Alert")),
    ("Local Testing",        (AppiumBy.NAME, "Local Testing")),
    ("Web View",             (AppiumBy.NAME, "Web View")),
    ("nav_ui",               (AppiumBy.NAME, "nav_ui")),
]

print("\nTrying candidate locators:")
for label, locator in candidates:
    by, val = locator
    try:
        el = driver.find_element(by, val)
        print(f"- FOUND by {by}: '{val}'  -> tag: {el.tag_name} text/value: '{el.text or el.get_attribute('value')}'")
    except Exception as e:
        print(f"- NOT FOUND by {by}: '{val}'  ({e.__class__.__name__})")

print("\nTrying predicate examples for 'Text' and 'Text Button':")
try:
    el = driver.find_element(AppiumBy.IOS_PREDICATE, 'label == "Text"')
    print("- FOUND by IOS_PREDICATE label == 'Text'")
except Exception:
    print("- NOT FOUND: IOS_PREDICATE label == 'Text'")

try:
    el = driver.find_element(AppiumBy.IOS_PREDICATE, 'name == "Text Button"')
    print("- FOUND by IOS_PREDICATE name == 'Text Button'")
except Exception:
    print("- NOT FOUND: IOS_PREDICATE name == 'Text Button'")

print("\nSaving screenshot and page source to artifacts/")
os.makedirs("artifacts", exist_ok=True)
driver.save_screenshot("artifacts/check_locators_screenshot.png")
with open("artifacts/check_locators_pagesource.xml", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

print("Session ID:", driver.session_id)
driver.quit()
print("Done")

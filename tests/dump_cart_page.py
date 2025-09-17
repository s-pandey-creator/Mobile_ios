# tests/dump_cart_page.py
import os, sys, time

# ensure project root is on PYTHONPATH so "from pages..." imports work
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from appium import webdriver
from appium.options.common import AppiumOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy

# env vars (make sure these are set)
USERNAME = os.environ.get("BROWSERSTACK_USERNAME") or os.environ.get("BROWSERSTACK_USER")
ACCESS_KEY = os.environ.get("BROWSERSTACK_ACCESS_KEY") or os.environ.get("BROWSERSTACK_KEY")
APP_ID = os.environ.get("APP_ID") or os.environ.get("BROWSERSTACK_APP")
DEVICE = os.environ.get("DEVICE", "iPhone 14")
OS_VERSION = os.environ.get("OS_VERSION", "18")

if not USERNAME or not ACCESS_KEY or not APP_ID:
    raise SystemExit("Set BROWSERSTACK_USERNAME, BROWSERSTACK_ACCESS_KEY and APP_ID (or aliases) before running")

opts = AppiumOptions()
caps = {
    "bstack:options": {
        "userName": USERNAME,
        "accessKey": ACCESS_KEY,
        "deviceName": DEVICE,
        "osVersion": OS_VERSION,
        "appiumVersion": "2.0.0",
        "projectName": "Mobile-Automation",
        "buildName": "cart-dump",
        "sessionName": "dump-cart-page"
    },
    "app": APP_ID,
    "automationName": "XCUITest"
}
opts.load_capabilities(caps)

hub = "https://hub-cloud.browserstack.com/wd/hub"
print("Starting BrowserStack session for cart dump...")
driver = webdriver.Remote(command_executor=hub, options=opts)

try:
    wait = WebDriverWait(driver, 20)

    # login
    print("Logging in...")
    from pages.login_page import LoginPage
    lp = LoginPage(driver)
    lp.login("standard_user", "secret_sauce")

    # add first product
    print("Adding first product to cart...")
    from pages.products_page import ProductsPage
    pp = ProductsPage(driver)
    pp.wait_for_products()
    try:
        pp.add_first_product_to_cart()
    except Exception as e:
        print("Warning: add_first_product_to_cart() raised:", e)

    # open cart
    print("Opening cart...")
    from pages.cart_page import CartPage
    cart = CartPage(driver)
    try:
        cart.open_cart()
    except Exception as e:
        print("Warning: open_cart() raised:", e)

    # small pause to let cart render
    time.sleep(1)

    # save page source + screenshot
    os.makedirs("artifacts", exist_ok=True)
    pagesrc_path = os.path.join("artifacts", "pagesource_cart.xml")
    screenshot_path = os.path.join("artifacts", "screenshot_cart.png")
    with open(pagesrc_path, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.save_screenshot(screenshot_path)

    print(f"Saved cart page source -> {pagesrc_path}")
    print(f"Saved screenshot -> {screenshot_path}")

finally:
    driver.quit()

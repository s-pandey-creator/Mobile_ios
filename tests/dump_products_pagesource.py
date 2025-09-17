# tests/dump_products_pagesource.py
import os
from datetime import datetime
import pytest
from pages.login_page import LoginPage
from pages.products_page import ProductsPage

def _timestamp():
    return datetime.utcnow().strftime("%Y%m%dT%H%M%S")

def test_dump_products_pagesource(driver):
    """Login, wait for product list, save page source + screenshot for debugging."""
    lp = LoginPage(driver)
    # use your valid creds
    lp.login("standard_user", "secret_sauce")

    pp = ProductsPage(driver)
    pp.wait_for_products()

    ts = _timestamp()
    artifacts_dir = os.path.join(os.getcwd(), "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    src = os.path.join(artifacts_dir, f"dump_products_pagesource_{ts}.xml")
    png = os.path.join(artifacts_dir, f"dump_products_screenshot_{ts}.png")

    try:
        with open(src, "w", encoding="utf-8") as f:
            f.write(driver.page_source or "")
    except Exception as e:
        print("Failed to save page source:", e)
        src = "(failed)"

    try:
        driver.get_screenshot_as_file(png)
    except Exception as e:
        print("Failed to save screenshot:", e)
        png = "(failed)"

    print(f"Saved page source -> {src}")
    print(f"Saved screenshot  -> {png}")
    # keep test green so it's only used for debugging
    assert True

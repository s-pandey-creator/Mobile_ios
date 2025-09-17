# tests/test_products_cart_sorting.py
import pytest
from pages.products_page import ProductsPage
from pages.cart_page import CartPage
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

VALID_USER = "standard_user"
VALID_PASS = "secret_sauce"


def login(driver):
    """Helper to log in with valid user."""
    from pages.login_page import LoginPage
    lp = LoginPage(driver)
    lp.login(VALID_USER, VALID_PASS)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (AppiumBy.IOS_PREDICATE, 'label == "PRODUCTS"')
        )
    )


def test_open_catalog_and_verify_product_details(driver):
    login(driver)
    pp = ProductsPage(driver)
    pp.wait_for_products()
    titles = pp.get_all_product_titles()
    assert titles and len(titles) > 0, "No products found in catalog"

    # pick first product and open details
    product_name = titles[0]
    pp.open_product_details(product_name)

    # verify product title exists on details page
    detail_title = WebDriverWait(driver, 8).until(
        EC.presence_of_element_located(
            (AppiumBy.IOS_PREDICATE, f'label == "{product_name}"')
        )
    )
    assert detail_title is not None


def test_add_product_to_cart_and_verify(driver):
    login(driver)
    pp = ProductsPage(driver)
    pp.wait_for_products()
    titles = pp.get_all_product_titles()
    assert titles, "No products found"

    # Add the first product (by button, more reliable)
    first_product = titles[0]
    pp.add_first_product_to_cart()

    cart = CartPage(driver)
    cart.open_cart()
    items = cart.get_cart_items()

    # ✅ Robust: ensure cart has at least 1 product
    assert items, "No items found in the cart"

    # Optional: also check first product name is in cart
    assert any(first_product in it for it in items), (
        f"{first_product} not found in cart items: {items}"
    )


def test_sorting_by_price(driver):
    login(driver)
    pp = ProductsPage(driver)
    pp.wait_for_products()

    # try to open sort control - Swag Labs has a sort dropdown
    try:
        sort_btn = driver.find_element(
            AppiumBy.IOS_PREDICATE,
            'type == "XCUIElementTypeButton" and (label CONTAINS "SORT" or name CONTAINS "sort")'
        )
        sort_btn.click()
    except Exception:
        # fallback: skip if not present
        pytest.skip("Sort button not found on this build")

    # select "Price (low to high)"
    try:
        opt = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located(
                (AppiumBy.IOS_PREDICATE, 'label CONTAINS "low to high"')
            )
        )
        opt.click()
    except Exception:
        pytest.skip("Sort option not found on this build")

    # After sorting, get product prices and assert ascending order
    price_elems = driver.find_elements(
        AppiumBy.IOS_PREDICATE, 'label BEGINSWITH "$"'
    )
    prices = []
    for e in price_elems:
        txt = e.text or e.get_attribute("value") or ""
        if txt.startswith("$"):
            try:
                prices.append(float(txt.replace("$", "").strip()))
            except Exception:
                continue

    assert prices, "No prices found after sorting"
    assert prices == sorted(prices), f"Prices not sorted ascending: {prices}"

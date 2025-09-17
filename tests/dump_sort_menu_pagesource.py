# tests/dump_sort_menu_pagesource.py
import os
from datetime import datetime
import time
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from pages.login_page import LoginPage
from pages.products_page import ProductsPage

def _timestamp():
    return datetime.utcnow().strftime("%Y%m%dT%H%M%S")

def _save_artifacts(driver, prefix):
    ts = _timestamp()
    artifacts_dir = os.path.join(os.getcwd(), "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    src = os.path.join(artifacts_dir, f"{prefix}_pagesource_{ts}.xml")
    png = os.path.join(artifacts_dir, f"{prefix}_screenshot_{ts}.png")
    try:
        with open(src, "w", encoding="utf-8") as f:
            f.write(driver.page_source or "")
    except Exception as e:
        src = f"(failed to save pagesource: {e})"
    try:
        driver.get_screenshot_as_file(png)
    except Exception as e:
        png = f"(failed to save screenshot: {e})"
    return src, png

def test_dump_sort_menu_pagesource(driver):
    lp = LoginPage(driver)
    lp.login("standard_user", "secret_sauce")

    pp = ProductsPage(driver)
    pp.wait_for_products()

    # Try to click the modal selector button using several strategies.
    clicked = False
    reasons = []

    # 1) accessibility id (preferred)
    try:
        el = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Modal Selector Button")
        try:
            el.click()
            clicked = True
            reasons.append("clicked by ACCESSIBILITY_ID")
        except Exception:
            # fallback tap by element center if click fails
            try:
                driver.execute_script("mobile: tap", {"element": el.id})
                clicked = True
                reasons.append("tapped element by id")
            except Exception as e:
                reasons.append(f"accessibility id found but click failed: {e}")
    except Exception as e:
        reasons.append(f"no element by ACCESSIBILITY_ID: {e}")

    # 2) try iOS predicate name/label if not clicked
    if not clicked:
        try:
            el = driver.find_element(AppiumBy.IOS_PREDICATE, "name == 'test-Modal Selector Button' OR label CONTAINS 'Modal Selector' OR name CONTAINS 'Modal Selector'")
            try:
                el.click()
                clicked = True
                reasons.append("clicked by IOS_PREDICATE")
            except Exception:
                try:
                    driver.execute_script("mobile: tap", {"element": el.id})
                    clicked = True
                    reasons.append("tapped element by IOS_PREDICATE")
                except Exception as e:
                    reasons.append(f"predicate found but click failed: {e}")
        except Exception as e:
            reasons.append(f"no element by IOS_PREDICATE: {e}")

    # 3) coordinate tap fallback (use coordinates observed earlier as center)
    # These coordinates are conservative; if your screen size differs adjust them.
    if not clicked:
        try:
            # center coords seen in pagesource: x=325,y=116 width=41 height=41 -> center ~ (346,136)
            x = int(os.environ.get("TEST_MODAL_FALLBACK_X", "346"))
            y = int(os.environ.get("TEST_MODAL_FALLBACK_Y", "136"))
            try:
                driver.execute_script("mobile: tap", {"x": x, "y": y})
                clicked = True
                reasons.append(f"tapped coords {x},{y}")
            except Exception as e:
                reasons.append(f"coordinate tap failed: {e}")
        except Exception as e:
            reasons.append(f"coordinate tap setup failed: {e}")

    # wait briefly for modal contents to render (no hard sleep for long)
    if clicked:
        # short explicit wait loop polling page_source to show new texts (non-blocking)
        found = False
        for _ in range(6):  # ~ up to 6 * 0.5s = 3s polling
            src = driver.page_source or ""
            lower = src.lower()
            if "price" in lower or "low to high" in lower or "price (low to high)" in lower or "sort" in lower:
                found = True
                break
            time.sleep(0.5)
        reasons.append(f"modal_detected={found}")
    else:
        reasons.append("not clicked")

    # Save artifacts after attempt
    src_path, png_path = _save_artifacts(driver, "dump_sort_menu_after_click")
    print("CLICK_ATTEMPT_REASONS:", reasons)
    print("Saved page source ->", src_path)
    print("Saved screenshot  ->", png_path)

    # keep test green for debugging
    assert True

# tests/dump_page_source.py
import os, time, json
from datetime import datetime
from appium import webdriver
# Try importing AppiumOptions from the most likely paths
try:
    from appium.options.common.base import AppiumOptions
except Exception:
    try:
        from appium.options.appium_options import AppiumOptions
    except Exception:
        # fallback minimal options object
        class AppiumOptions(dict):
            def set_capability(self, k, v):
                self[k] = v
            def to_capabilities(self):
                return dict(self)

def ts():
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

def save_text(name, text):
    with open(name, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[SAVED] {name}")

def try_click(driver, by, val, wait=5):
    """
    Non-failing attempt to find and click element; returns True if clicked.
    We use a few strategies with execute_script fallback.
    """
    from appium.webdriver.common.appiumby import AppiumBy
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    locator = None
    by_lower = by.lower()
    try:
        if by_lower in ("accessibility id", "accessibility_id"):
            locator = (AppiumBy.ACCESSIBILITY_ID, val)
        elif by_lower == "id":
            locator = (AppiumBy.ID, val)
        elif by_lower == "name":
            locator = (AppiumBy.ACCESSIBILITY_ID, val)
        elif by_lower in ("-ios predicate string", "ios predicate string"):
            locator = (AppiumBy.IOS_PREDICATE, val)
        elif by_lower == "xpath":
            locator = (AppiumBy.XPATH, val)
        else:
            locator = (AppiumBy.XPATH, val)

        el = WebDriverWait(driver, wait).until(EC.element_to_be_clickable(locator))
        el.click()
        print(f"[CLICKED] {by}='{val}'")
        return True
    except Exception as e:
        # try script tap fallback
        try:
            print(f"[TRY SCRIPT TAP] fallback for {by}='{val}' -> {e}")
            # best-effort: try find element by xpath containing text and tap coordinates
            if by_lower in ("accessibility id", "name"):
                xp = f"//*[@name='{val}' or @label='{val}']"
            else:
                xp = val
            els = driver.find_elements_by_xpath(xp)
            if els:
                el = els[0]
                driver.execute_script("mobile: tap", {"element": el.id})
                print(f"[SCRIPT TAP] via xpath {xp}")
                return True
        except Exception:
            pass
    return False

def main():
    user = os.environ.get("BROWSERSTACK_USERNAME")
    key = os.environ.get("BROWSERSTACK_ACCESS_KEY")
    app = os.environ.get("BROWSERSTACK_APP")
    if not (user and key and app):
        print("Please set BROWSERSTACK_USERNAME, BROWSERSTACK_ACCESS_KEY and BROWSERSTACK_APP in this shell.")
        return

    # Build options (works across appium client versions)
    try:
        opts = AppiumOptions()
    except Exception:
        opts = AppiumOptions()

    # Minimal capabilities (we rely on your defaults from conftest)
    opts.set_capability("platformName", os.environ.get("DUMP_PLATFORM", "iOS"))
    opts.set_capability("deviceName", os.environ.get("DUMP_DEVICE", "iPhone 14"))
    opts.set_capability("app", app)
    # set BrowserStack options explicitly
    bstack = {
        "userName": user,
        "accessKey": key,
        "sessionName": f"dump-page-source-{ts()}"
    }
    try:
        # AppiumOptions may accept load_capabilities
        opts.load_capabilities({"bstack:options": bstack})
    except Exception:
        opts.set_capability("bstack:options", bstack)

    hub = "https://hub-cloud.browserstack.com/wd/hub"
    print("[INFO] Starting remote session...")
    driver = webdriver.Remote(hub, options=opts)

    try:
        time.sleep(5)  # allow app to settle
        # Save initial page source + screenshot
        initial_src = driver.page_source
        fname_src = f"page_source_initial_{ts()}.xml"
        save_text(fname_src, initial_src)
        try:
            ss = f"screenshot_initial_{ts()}.png"
            driver.save_screenshot(ss)
            print(f"[SAVED] {ss}")
        except Exception as e:
            print("[WARN] could not save screenshot:", e)

        # Define targets we try to click (products, cart, ui elements)
        targets = {
            "products": [
                ("accessibility id", "Products"),
                ("accessibility id", "test-Products"),
                ("xpath", "//*[contains(., 'Products') or contains(., 'PRODUCTS')]"),
                ("-ios predicate string", "label CONTAINS 'Products' or name CONTAINS 'Products'")
            ],
            "cart": [
                ("accessibility id", "test-Cart"),
                ("accessibility id", "Cart"),
                ("name", "test-Cart"),
                ("-ios predicate string", "label CONTAINS 'Cart' or name CONTAINS 'Cart'"),
                ("xpath", "//*[contains(translate(@label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'cart') or contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'cart')]")
            ],
            "ui_elements": [
                ("accessibility id", "UI Elements"),
                ("accessibility id", "test-UI Elements"),
                ("xpath", "//*[contains(., 'UI Elements') or contains(., 'UI elements') or contains(., 'UI ELEMENTS')]"),
                ("-ios predicate string", "label CONTAINS 'UI' and label CONTAINS 'Elements'")
            ]
        }

        for name, cands in targets.items():
            clicked = False
            for by, val in cands:
                if try_click(driver, by, val, wait=4):
                    clicked = True
                    time.sleep(3)  # allow navigation
                    src = driver.page_source
                    fname = f"page_source_{name}_{ts()}.xml"
                    save_text(fname, src)
                    try:
                        ssf = f"screenshot_{name}_{ts()}.png"
                        driver.save_screenshot(ssf)
                        print(f"[SAVED] {ssf}")
                    except Exception as e:
                        print("[WARN] could not save screenshot:", e)
                    break
            print(f"[INFO] target='{name}' clicked? {clicked}")

    finally:
        try:
            driver.quit()
        except Exception:
            pass
        print("[INFO] session ended")

if __name__ == "__main__":
    main()

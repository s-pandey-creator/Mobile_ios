# pages/products_page.py
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

class ProductsPage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout
        self.PRODUCTS_HEADER = (AppiumBy.IOS_PREDICATE, 'label == "PRODUCTS"')
        self.PRODUCT_ITEM = (AppiumBy.IOS_PREDICATE, "label CONTAINS 'ADD TO CART' OR label CONTAINS '$'")

    def wait_for_products(self):
        try:
            WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(self.PRODUCTS_HEADER))
            return True
        except Exception:
            return self.exists(self.PRODUCT_ITEM, timeout=min(self.timeout, 8))

    def exists(self, locator, timeout=3):
        by, val = locator
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, val)))
            return True
        except Exception:
            return False

    def get_all_product_titles(self):
        titles = []
        try:
            els = self.driver.find_elements(AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeStaticText' and (label CONTAINS 'Sauce' or label CONTAINS 'Test.allTheThings' or name CONTAINS 'test-Item title')")
            for e in els:
                txt = (e.text or e.get_attribute("label") or "").strip()
                if txt and txt not in titles:
                    titles.append(txt)
        except Exception:
            pass
        if not titles:
            try:
                items = self.driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "test-Item")
                for it in items:
                    try:
                        t = it.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Item title")
                        txt = (t.text or t.get_attribute("label") or "").strip()
                        if txt:
                            titles.append(txt)
                    except Exception:
                        continue
            except Exception:
                pass
        return titles

    def open_product_details(self, product_name):
        try:
            el = self.driver.find_element(AppiumBy.IOS_PREDICATE, f'label == "{product_name}"')
            el.click()
            return True
        except Exception:
            try:
                el = self.driver.find_element(AppiumBy.XPATH, f"//XCUIElementTypeStaticText[contains(translate(@label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{product_name.lower()}')]")
                el.click()
                return True
            except Exception:
                return False

    def add_first_product_to_cart(self):
        try:
            items = self.driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "test-Item")
            if items:
                first = items[0]
                try:
                    title_el = first.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Item title")
                    title = (title_el.text or title_el.get_attribute("label") or "").strip()
                except Exception:
                    title = ""
                try:
                    btn = first.find_element(AppiumBy.ACCESSIBILITY_ID, "test-ADD TO CART")
                    btn.click()
                    return title
                except Exception:
                    try:
                        btn2 = first.find_element(AppiumBy.IOS_PREDICATE, "label CONTAINS 'ADD TO CART'")
                        btn2.click()
                        return title
                    except Exception:
                        pass
        except Exception:
            pass
        try:
            btns = self.driver.find_elements(AppiumBy.IOS_PREDICATE, "label CONTAINS 'ADD TO CART'")
            if btns:
                try:
                    parent = btns[0].find_element(AppiumBy.XPATH, "ancestor::XCUIElementTypeOther")
                    title = ""
                    try:
                        t = parent.find_element(AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeStaticText' and (label CONTAINS 'Sauce' OR label CONTAINS 'Test.allTheThings')")
                        title = (t.text or t.get_attribute("label") or "").strip()
                    except Exception:
                        title = ""
                except Exception:
                    title = ""
                try:
                    btns[0].click()
                except Exception:
                    try:
                        self.driver.execute_script("mobile: tap", {"element": btns[0].id})
                    except Exception:
                        pass
                return title
        except Exception:
            pass
        return ""

    # ----------------- SORT helpers -----------------
    def is_sort_present(self, timeout=3):
        candidates = [
            (AppiumBy.ACCESSIBILITY_ID, "test-Modal Selector Button"),
            (AppiumBy.ACCESSIBILITY_ID, "test-Sort"),
            (AppiumBy.IOS_PREDICATE, "label CONTAINS 'Sort' OR label CONTAINS 'Sort By'"),
            (AppiumBy.XPATH, "//*[contains(translate(@label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sort') or contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sort') or contains(translate(@content-desc,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sort')]"),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("sort")')
        ]
        for by, val in candidates:
            try:
                WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, val)))
                return True
            except Exception:
                continue
        return False

    def open_sort_menu(self):
        candidates = [
            (AppiumBy.ACCESSIBILITY_ID, "test-Modal Selector Button"),
            (AppiumBy.ACCESSIBILITY_ID, "test-Sort"),
            (AppiumBy.IOS_PREDICATE, "label CONTAINS 'Sort'"),
            (AppiumBy.XPATH, "//*[contains(translate(@label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sort') or contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sort') or contains(translate(@content-desc,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sort')]"),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("sort")')
        ]
        for by, val in candidates:
            try:
                el = self.driver.find_element(by, val)
                try:
                    el.click()
                except Exception:
                    try:
                        self.driver.execute_script("mobile: tap", {"element": el.id})
                    except Exception:
                        pass
                return True
            except Exception:
                continue
        # fallback: open menu and look for sort inside it
        try:
            menu = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Menu")
            try:
                menu.click()
            except Exception:
                pass
            try:
                s = self.driver.find_element(AppiumBy.XPATH, "//*[contains(translate(@label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sort') or contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sort')]")
                try:
                    s.click()
                except Exception:
                    pass
                return True
            except Exception:
                pass
        except Exception:
            pass
        return False

    def select_sort_option(self, option_text="Price (low to high)"):
        """Select the given option shown in the selector modal.

        This build exposes the options as 'Name (A to Z)', 'Name (Z to A)',
        'Price (low to high)', 'Price (high to low)' (seen as accessible labels).
        We try ACCESSIBILITY_ID first for exact match, then fallbacks.
        """
        # 1) exact accessibility id / label match (observed in pagesource)
        try:
            el = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, option_text))
            )
            try:
                el.click()
            except Exception:
                try:
                    self.driver.execute_script("mobile: tap", {"element": el.id})
                except Exception:
                    pass
            return True
        except Exception:
            pass

        # 2) try static text match (case-insensitive contains)
        try:
            xpath = f"//XCUIElementTypeOther[contains(translate(@label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{option_text.lower()}') or contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{option_text.lower()}') or contains(translate(@value,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{option_text.lower()}')]"
            el = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((AppiumBy.XPATH, xpath)))
            try:
                el.click()
            except Exception:
                try:
                    self.driver.execute_script("mobile: tap", {"element": el.id})
                except Exception:
                    pass
            return True
        except Exception:
            pass

        # 3) short keyword matches (e.g., 'low to high', 'price')
        short_cands = ["low to high", "price (low", "price"]
        for kw in short_cands:
            try:
                el = self.driver.find_element(AppiumBy.XPATH, f"//*[contains(translate(@label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{kw}') or contains(translate(@text,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{kw}')]")
                try:
                    el.click()
                except Exception:
                    pass
                return True
            except Exception:
                continue

        return False

    def collect_visible_prices(self):
        prices = []
        try:
            els = self.driver.find_elements(AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeStaticText' AND label CONTAINS '$'")
            for e in els:
                txt = (e.text or e.get_attribute("label") or "").strip()
                if txt:
                    m = re.search(r"[\d,]+(?:\.\d+)?", txt.replace(",", ""))
                    if m:
                        try:
                            prices.append(float(m.group().replace(",", "")))
                        except Exception:
                            continue
        except Exception:
            pass

        if not prices:
            try:
                els2 = self.driver.find_elements(AppiumBy.XPATH, "//*[contains(text(),'$') or contains(text(),'₹') or contains(text(),'Rs') or contains(@label,'$')]")
                for e in els2:
                    txt = (e.text or e.get_attribute("label") or "").strip()
                    if not txt:
                        continue
                    m = re.search(r"[\d,]+(?:\.\d+)?", txt.replace(",", ""))
                    if m:
                        try:
                            prices.append(float(m.group().replace(",", "")))
                        except Exception:
                            continue
            except Exception:
                pass

        if not prices:
            try:
                statics = self.driver.find_elements(AppiumBy.XPATH, "//XCUIElementTypeStaticText | //android.widget.TextView")
                for s in statics:
                    txt = (s.text or s.get_attribute("label") or "").strip()
                    if not txt:
                        continue
                    m = re.search(r"[\d,]+(?:\.\d+)?", txt.replace(",", ""))
                    if m:
                        try:
                            prices.append(float(m.group().replace(",", "")))
                        except Exception:
                            continue
            except Exception:
                pass

        return prices


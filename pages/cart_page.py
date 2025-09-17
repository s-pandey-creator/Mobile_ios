# pages/cart_page.py
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CartPage:
    def __init__(self, driver, timeout=8):
        self.driver = driver
        self.timeout = timeout
        self.cart_btn_candidates = [
            (AppiumBy.ACCESSIBILITY_ID, "test-Cart"),
            (AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeButton' and label CONTAINS 'Cart'")
        ]
        self.item_title_pred = (
            "type == 'XCUIElementTypeStaticText' and label CONTAINS 'Sauce'"
        )

    def open_cart(self):
        for by, val in self.cart_btn_candidates:
            try:
                btn = WebDriverWait(self.driver, 6).until(
                    EC.presence_of_element_located((by, val))
                )
                btn.click()
                WebDriverWait(self.driver, 6).until(
                    EC.presence_of_element_located(
                        (AppiumBy.IOS_PREDICATE, "label CONTAINS 'YOUR CART'")
                    )
                )
                return True
            except Exception:
                continue
        return False

    def get_cart_items(self):
        items = []
        try:
            els = self.driver.find_elements(AppiumBy.IOS_PREDICATE, self.item_title_pred)
            for e in els:
                txt = (e.text or e.get_attribute("label") or "").strip()
                if txt and txt not in items:
                    items.append(txt)
        except Exception:
            pass
        return items

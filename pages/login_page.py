# pages/login_page.py
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class LoginPage:
    """
    Robust LoginPage for Swag Labs mobile. Tolerant of variations in element types/labels.
    """

    def __init__(self, driver, timeout=12):
        self.driver = driver
        self.timeout = timeout

        # candidate locators for username/password/login
        self.username_candidates = [
            (AppiumBy.ACCESSIBILITY_ID, "test-Username"),
            (AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeTextField' AND (label CONTAINS 'username' OR name CONTAINS 'username' OR value CONTAINS 'username')"),
            (AppiumBy.XPATH, "//XCUIElementTypeTextField"),
        ]
        self.password_candidates = [
            (AppiumBy.ACCESSIBILITY_ID, "test-Password"),
            (AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeSecureTextField' AND (label CONTAINS 'password' OR name CONTAINS 'password' OR value CONTAINS 'password')"),
            (AppiumBy.XPATH, "//XCUIElementTypeSecureTextField"),
        ]
        self.login_btn_candidates = [
            (AppiumBy.ACCESSIBILITY_ID, "test-LOGIN"),
            (AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeButton' AND (label CONTAINS 'LOGIN' OR name CONTAINS 'LOGIN' OR label CONTAINS 'Log in' OR label CONTAINS 'Log In')"),
            (AppiumBy.XPATH, "//XCUIElementTypeButton[contains(translate(@label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'login') or contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'login')]")
        ]

        # error candidate patterns (broad)
        self.error_candidates = [
            (AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeStaticText' AND (label CONTAINS 'error' OR value CONTAINS 'error' OR label CONTAINS 'invalid' OR value CONTAINS 'invalid' OR label CONTAINS 'Username' OR label CONTAINS 'do not match')"),
            (AppiumBy.XPATH, "//XCUIElementTypeStaticText[contains(translate(@label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'invalid') or contains(translate(@label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'do not match') or contains(translate(@label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'username')]"),
            # generic modal/alert nodes
            (AppiumBy.XPATH, "//*[contains(translate(@label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'epic sadface') or contains(translate(@label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'username and password do not match') or contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'username and password do not match')]")
        ]

    def _find_first(self, candidates, timeout=None):
        """Return first element found from candidates or None."""
        timeout = timeout or self.timeout
        for by, val in candidates:
            try:
                el = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((by, val)))
                if el:
                    return el
            except Exception:
                continue
        return None

    def _try_click(self, el):
        """Try click(), then mobile: tap fallback."""
        if el is None:
            return False
        try:
            el.click()
            return True
        except Exception:
            # fallback to mobile tap by element id or coordinates
            try:
                if hasattr(el, "id") and el.id:
                    self.driver.execute_script("mobile: tap", {"element": el.id})
                    return True
            except Exception:
                pass
            try:
                rect = {}
                try:
                    rect = el.rect
                except Exception:
                    rect = {
                        "x": int(el.get_attribute("x") or 0),
                        "y": int(el.get_attribute("y") or 0),
                        "width": int(el.get_attribute("width") or 0),
                        "height": int(el.get_attribute("height") or 0)
                    }
                cx = int(rect.get("x", 0) + rect.get("width", 0) / 2)
                cy = int(rect.get("y", 0) + rect.get("height", 0) / 2)
                if cx and cy:
                    self.driver.execute_script("mobile: tap", {"x": cx, "y": cy})
                    return True
            except Exception:
                pass
        return False

    def login(self, username, password):
        """Type credentials and press login. Raises if core controls missing."""
        u = self._find_first(self.username_candidates)
        p = self._find_first(self.password_candidates)
        btn = self._find_first(self.login_btn_candidates)

        if u is None or p is None or btn is None:
            # try a last-chance direct finds (longer wait) before failing
            try:
                u = WebDriverWait(self.driver, 3).until(lambda d: d.find_element(*self.username_candidates[0]))
            except Exception:
                pass
            try:
                p = WebDriverWait(self.driver, 3).until(lambda d: d.find_element(*self.password_candidates[0]))
            except Exception:
                pass
            try:
                btn = WebDriverWait(self.driver, 3).until(lambda d: d.find_element(*self.login_btn_candidates[0]))
            except Exception:
                pass

        if u is None or p is None or btn is None:
            raise RuntimeError("Login page controls not found (username/password/login)")

        # try typing; some fields require clear first
        try:
            u.clear()
        except Exception:
            pass
        u.send_keys(username)

        try:
            p.clear()
        except Exception:
            pass
        p.send_keys(password)

        # click login with fallback
        clicked = self._try_click(btn)
        if not clicked:
            # as last resort, try to send ENTER on password field (some builds accept it)
            try:
                p.send_keys("\n")
                clicked = True
            except Exception:
                pass

        return clicked

    def get_error_text(self, wait_seconds=4):
        """Return the best-effort error text after a login attempt.

        This polls for up to wait_seconds and checks:
         - explicit error candidates,
         - alert/modal containers,
         - any visible static text that looks like an error.
        """
        deadline = time.time() + (wait_seconds or 4)
        last = ""
        while time.time() < deadline:
            # 1) check explicit candidate locators
            for by, val in self.error_candidates:
                try:
                    el = self.driver.find_element(by, val)
                    if el:
                        txt = (el.text or el.get_attribute("label") or el.get_attribute("value") or "").strip()
                        if txt:
                            return txt
                except Exception:
                    continue

            # 2) check standard iOS alert/body nodes for common phrases
            try:
                # look for nodes that contain the whole selector text (as observed)
                els = self.driver.find_elements(AppiumBy.XPATH, "//XCUIElementTypeOther | //XCUIElementTypeStaticText")
                for e in els[:40]:
                    try:
                        txt = (e.text or e.get_attribute("label") or e.get_attribute("value") or "").strip()
                        if not txt:
                            continue
                        lower = txt.lower()
                        if ("invalid" in lower) or ("do not match" in lower) or ("epic sadface" in lower) or ("username" in lower and "password" in lower) or ("required" in lower):
                            return txt
                    except Exception:
                        continue
            except Exception:
                pass

            # 3) broad scan of static text nodes picking anything that looks like an error
            try:
                statics = self.driver.find_elements(AppiumBy.XPATH, "//XCUIElementTypeStaticText")
                for s in statics[:60]:
                    try:
                        txt = (s.text or s.get_attribute("label") or s.get_attribute("value") or "").strip()
                        if not txt:
                            continue
                        lower = txt.lower()
                        if any(k in lower for k in ("invalid", "error", "do not match", "epic sadface", "username and password", "required", "locked")):
                            return txt
                        # small heuristic to avoid returning generic UI text: require short length or presence of keywords
                        if len(txt) < 60 and ("!" in txt or "error" in lower):
                            return txt
                    except Exception:
                        continue
            except Exception:
                pass

            # nothing yet — poll a short time
            time.sleep(0.35)

        # final fallback: return empty string
        return ""

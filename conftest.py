# conftest.py
import os
import pytest
from datetime import datetime

# Appium / Selenium imports
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Try importing AppiumOptions from likely locations (compatible with multiple client versions)
try:
    # appium-python-client >= 3.x
    from appium.options.common.base import AppiumOptions
except Exception:
    try:
        # older packaging path
        from appium.options.appium_options import AppiumOptions
    except Exception:
        # minimal fallback options-like object
        class AppiumOptions(dict):
            def set_capability(self, k, v):
                self[k] = v
            def to_capabilities(self):
                return dict(self)
            def load_capabilities(self, caps):
                for k, v in caps.items():
                    self.set_capability(k, v)

# Default BrowserStack creds (override with env vars in CI)
DEFAULT_BS_USER = os.environ.get("BROWSERSTACK_USERNAME", "sandeeppandey_3z5YkG")
DEFAULT_BS_KEY = os.environ.get("BROWSERSTACK_ACCESS_KEY", "7aU6Ny4pQdqVnJa8XxUw")
DEFAULT_BS_APP = os.environ.get("BROWSERSTACK_APP", "bs://bb87d435f3c19f20eb1118f1fe1145e35f0cd405")

ARTIFACTS_DIR = os.path.join(os.getcwd(), "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def _timestamp():
    return datetime.utcnow().strftime("%Y%m%dT%H%M%S")

def _save_debug(driver, prefix="debug"):
    """Save pagesource and screenshot to artifacts and return paths."""
    ts = _timestamp()
    src_name = f"{prefix}_pagesource_{ts}.xml"
    png_name = f"{prefix}_screenshot_{ts}.png"
    src_path = os.path.join(ARTIFACTS_DIR, src_name)
    png_path = os.path.join(ARTIFACTS_DIR, png_name)
    try:
        with open(src_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source or "")
    except Exception as e:
        src_path = f"(failed to save page_source: {e})"
    try:
        driver.get_screenshot_as_file(png_path)
    except Exception as e:
        png_path = f"(failed to save screenshot: {e})"
    return src_path, png_path

@pytest.fixture(scope="function")
def driver(request):
    """
    Function-scoped driver fixture.
    - Uses explicit waits to ensure login screen is ready (no hard sleeps).
    - Names BrowserStack session after the pytest test name.
    - Yields a fresh driver per test (reduces inter-test state bleed).
    """
    user = os.environ.get("BROWSERSTACK_USERNAME", DEFAULT_BS_USER)
    key = os.environ.get("BROWSERSTACK_ACCESS_KEY", DEFAULT_BS_KEY)
    app = os.environ.get("BROWSERSTACK_APP", DEFAULT_BS_APP)

    if not (user and key and app):
        raise RuntimeError("Set BROWSERSTACK_USERNAME, BROWSERSTACK_ACCESS_KEY and BROWSERSTACK_APP")

    # Build AppiumOptions in a way that works with different client versions
    try:
        opts = AppiumOptions()
    except Exception:
        opts = AppiumOptions()

    # Core caps (tweakable via env vars)
    opts.set_capability("platformName", os.environ.get("DUMP_PLATFORM", "iOS"))
    opts.set_capability("deviceName", os.environ.get("DUMP_DEVICE", "iPhone 14"))
    opts.set_capability("app", app)

    # BrowserStack options (bstack:options) — set session name per test
    bstack_opts = {
        "userName": user,
        "accessKey": key,
        "sessionName": request.node.name  # ensures video/session labelled with test name
    }
    try:
        opts.load_capabilities({"bstack:options": bstack_opts})
    except Exception:
        opts.set_capability("bstack:options", bstack_opts)

    hub = "https://hub-cloud.browserstack.com/wd/hub"

    # Create the driver
    driver = webdriver.Remote(command_executor=hub, options=opts)

    # ---------- EXPLICIT WAIT: wait until login screen is ready ----------
    # Wait for either the standard username accessibility id OR any text field as a fallback.
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "test-Username"))
        )
    except Exception:
        # fallback waiting for any textfield (no hard sleeps; explicit wait)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeTextField'"))
            )
        except Exception:
            # if still not found, save debug for investigation but continue to yield driver
            try:
                src, png = _save_debug(driver, prefix=f"driver_start_{request.node.name}")
                print(f"[conftest] login control not found during startup. Saved {src}, {png}")
            except Exception:
                pass

    # Set a small implicit wait for element find fallback tolerance (not a hard sleep)
    try:
        driver.implicitly_wait(3)
    except Exception:
        pass

    yield driver

    # Teardown: determine test result and mark BrowserStack session accordingly.
    # We rely on pytest_runtest_makereport hook below to set the session status.
    try:
        driver.quit()
    except Exception:
        pass

# Hook to capture test outcome and update BrowserStack session status + save artifacts on failure.
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    After each test phase, this hook runs. We care about the 'call' phase (test body).
    If test failed, save debug artifacts and mark BrowserStack session as failed via executor.
    If test passed, mark session passed.
    """
    outcome = yield
    rep = outcome.get_result()

    # only act after the actual test call (not setup/teardown)
    if rep.when != "call":
        return

    # get driver fixture if available
    driver_fixture = None
    try:
        driver_fixture = item.funcargs.get("driver")
    except Exception:
        driver_fixture = None

    # no driver -> nothing to do
    if not driver_fixture:
        return

    driver = driver_fixture

    # If test failed, save artifacts
    if rep.failed:
        try:
            src, png = _save_debug(driver, prefix=f"failure_{item.name}")
            print(f"[conftest] Test failed. Saved page_source -> {src}, screenshot -> {png}")
        except Exception:
            pass

        # Mark BrowserStack session as failed with reason
        try:
            reason = ""
            if hasattr(rep, "longrepr"):
                # concise reason
                reason = str(rep.longrepr).splitlines()[-1][:250]
            driver.execute_script(
                "browserstack_executor: {\"action\": \"setSessionStatus\", \"arguments\": {\"status\":\"failed\",\"reason\":\"%s\"}}"
                % reason
            )
        except Exception:
            pass
    else:
        # test passed -> mark session passed
        try:
            driver.execute_script(
                "browserstack_executor: {\"action\": \"setSessionStatus\", \"arguments\": {\"status\":\"passed\",\"reason\":\"All assertions passed\"}}"
            )
        except Exception:
            pass

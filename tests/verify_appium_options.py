# tests/verify_appium_options.py
import sys
import site
import pkgutil
import traceback

print("Python executable:", sys.executable)
print("sys.path (first 6 entries):")
for p in sys.path[:6]:
    print("  ", p)
print("site-packages locations:")
try:
    print("\n".join(site.getsitepackages()))
except Exception:
    print("  (site.getsitepackages not available)")

print("\n--- Installed package info ---")
import importlib
def show(pkg):
    try:
        m = importlib.import_module(pkg)
        print(f"{pkg}: module file -> {getattr(m, '__file__', '(builtin)')}")
    except Exception as e:
        print(f"{pkg}: import failed -> {e}")

for pkg in ("appium", "selenium", "urllib3"):
    show(pkg)

print("\n--- pip show output ---")
try:
    import subprocess, json, shlex
    for pkg in ("Appium-Python-Client", "selenium", "urllib3"):
        try:
            out = subprocess.check_output([sys.executable, "-m", "pip", "show", pkg], text=True)
            print(f"\n>> pip show {pkg}:\n{out}")
        except subprocess.CalledProcessError:
            print(f"\n>> pip show {pkg}: NOT INSTALLED")
except Exception as e:
    print("pip show step failed:", e)

print("\n--- Try import AppiumOptions from known paths ---")
paths = [
    "appium.options.appium_options",
    "appium.options.webdriver",
    "appium.webdriver.options.appium_options"
]
for p in paths:
    try:
        mod = __import__(p, fromlist=["AppiumOptions"])
        AO = getattr(mod, "AppiumOptions", None)
        print(f"Imported {p} -> AppiumOptions present? {AO is not None} (module: {getattr(mod,'__file__',None)})")
    except Exception as e:
        print(f"Import {p} FAILED -> {e}")

print("\n--- appium package location ---")
try:
    import appium
    print("appium.__file__ ->", appium.__file__)
except Exception as e:
    print("import appium failed ->", e)

print("\n--- Quick BrowserStack HEAD check (no auth) ---")
try:
    import urllib3
    http = urllib3.PoolManager(timeout=5.0)
    r = http.request("HEAD", "https://hub-cloud.browserstack.com/wd/hub")
    print("HEAD status:", r.status)
except Exception as e:
    print("HEAD check failed ->", e)

print("\nDone.")

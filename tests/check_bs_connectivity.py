# tests/check_bs_connectivity.py
import os
import json
import socket
import urllib.request
from urllib.error import HTTPError, URLError

def quick_dns(host="hub-cloud.browserstack.com"):
    try:
        return socket.getaddrinfo(host, 443)
    except Exception as e:
        return f"DNS resolution failed: {e}"

def quick_http_head(hub="https://hub-cloud.browserstack.com/wd/hub"):
    try:
        req = urllib.request.Request(hub, method="HEAD")
        with urllib.request.urlopen(req, timeout=7) as resp:
            return resp.status, resp.getheaders()
    except HTTPError as he:
        return f"HTTPError: {he.code}", he.read().decode(errors="ignore")
    except URLError as ue:
        return f"URLError: {ue}", None
    except Exception as e:
        return f"Error: {e}", None

def main():
    print("=== Environment ===")
    print("BROWSERSTACK_USERNAME:", os.environ.get("BROWSERSTACK_USERNAME"))
    print("BROWSERSTACK_ACCESS_KEY:", "SET" if os.environ.get("BROWSERSTACK_ACCESS_KEY") else "MISSING")
    print("BROWSERSTACK_APP:", os.environ.get("BROWSERSTACK_APP"))

    print("\n=== DNS check ===")
    print(quick_dns())

    print("\n=== HTTP HEAD check to BrowserStack hub ===")
    print(quick_http_head())

    print("\nIf DNS or HTTP fails: verify network/DNS or that your account/hub URL is correct.\n"
          "If AppiumOptions import fails when running pytest, run:\n"
          "  python -m pip install --upgrade \"Appium-Python-Client>=5.0.0\" selenium\n"
          "Then restart the shell (important) and retry pytest.")

if __name__ == "__main__":
    main()

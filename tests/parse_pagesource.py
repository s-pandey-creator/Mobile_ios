# tests/parse_pagesource.py
import xml.etree.ElementTree as ET
import sys

SRC = "artifacts/pagesource.xml"

try:
    tree = ET.parse(SRC)
except FileNotFoundError:
    print("Error: pagesource.xml not found. Run dump_page_source.py first.")
    sys.exit(1)

root = tree.getroot()

# helper to collect elements with useful attributes
candidates = []
for elem in root.iter():
    attrib = elem.attrib
    # common iOS attributes: accessibilityIdentifier, name, label, value
    acc = attrib.get("accessibilityIdentifier") or attrib.get("accessibility-id") or attrib.get("accessibilityId")
    name = attrib.get("name")
    label = attrib.get("label")
    value = attrib.get("value")
    if acc or name or label or value:
        text_preview = (attrib.get("text") or value or "")[:60]
        candidates.append({
            "tag": elem.tag,
            "accessibilityIdentifier": acc,
            "name": name,
            "label": label,
            "value": value,
            "text_preview": text_preview
        })

# print unique and usable candidates (deduplicate by tuple)
seen = set()
print("\nFound candidate locators (accessibility id / name / label / value):\n")
for c in candidates:
    key = (c["accessibilityIdentifier"], c["name"], c["label"], c["value"])
    if key in seen:
        continue
    seen.add(key)
    print(f"- accessibilityIdentifier: {c['accessibilityIdentifier']!s} | name: {c['name']!s} | label: {c['label']!s} | value: {c['value']!s} | text: {c['text_preview']!s}")

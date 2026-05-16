"""Read ODT file and print its text content"""
import zipfile
import xml.etree.ElementTree as ET

path = r"C:\Users\Gigabyte\Downloads\преддипломная. отчет.odt"

with zipfile.ZipFile(path) as z:
    with z.open("content.xml") as f:
        tree = ET.parse(f)

# Extract all text
ns = {"text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}
root = tree.getroot()

def get_text(elem):
    parts = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        parts.extend(get_text(child))
        if child.tail:
            parts.append(child.tail)
    return parts

lines = []
for p in root.iter():
    tag = p.tag.split("}")[-1] if "}" in p.tag else p.tag
    if tag in ("p", "h"):
        text = "".join(get_text(p)).strip()
        if text:
            lines.append(text)

with open(r"c:\Dev\METAai\odt_content.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Extracted {len(lines)} lines")
for i, line in enumerate(lines):
    print(f"{i+1}: {line}")

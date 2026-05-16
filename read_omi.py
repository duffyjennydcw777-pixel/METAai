import subprocess
import sys
try:
    from pypdf import PdfReader
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf", "-q"])
    from pypdf import PdfReader

pdf_path = r"C:\Users\Gigabyte\Downloads\Phone Link\OMI_brand_session_compilation_FINAL.pdf"
reader = PdfReader(pdf_path)
out = r"c:\Dev\METAai\omi_content.txt"
with open(out, "w", encoding="utf-8") as f:
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            f.write(f"\n--- PAGE {i+1} ---\n")
            f.write(text)
print(f"Done: {len(reader.pages)} pages -> {out}")

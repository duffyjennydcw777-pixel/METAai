"""
SATORI Ecosystem — Full Markdown → Luxury PDF converter v2
Fixes: base64 images, proper page breaks, mermaid → HTML tables
"""
import subprocess
import sys
import re
import os
import base64

for pkg in ["markdown", "playwright"]:
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

import markdown

MD_PATH = r"C:\Users\Gigabyte\.gemini\antigravity\brain\c308ccc7-b5ab-4ee4-b74e-d1dc1a24403c\SATORI_ECOSYSTEM_ANALYSIS.md"
HTML_PATH = r"c:\Dev\METAai\satori_report.html"
PDF_PATH = r"c:\Dev\METAai\SATORI_ECOSYSTEM_ANALYSIS.pdf"

with open(MD_PATH, "r", encoding="utf-8") as f:
    md_text = f.read()

# === IMAGES → base64 inline ===
def fix_img(m):
    alt = m.group(1)
    path = m.group(2).strip()
    if os.path.exists(path):
        ext = os.path.splitext(path)[1].lower().replace(".", "")
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(ext, "image/png")
        with open(path, "rb") as img_f:
            b64 = base64.b64encode(img_f.read()).decode()
        return f'<img src="data:{mime};base64,{b64}" alt="{alt}">'
    else:
        print(f"  ⚠ Image not found: {path}")
        return f'<p style="color:#C44536;">[Изображение не найдено: {alt}]</p>'

md_text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', fix_img, md_text)

# === MERMAID quadrantChart → HTML table ===
QUADRANT_HTML = """
<div class="competitive-map">
<h4 style="text-align:center;color:#C9A84C;margin-bottom:15px;">📊 Конкурентная карта Владикавказа</h4>
<table style="width:100%;">
<thead><tr><th>Игрок</th><th>Позиция (цена)</th><th>Позиция (специализация)</th><th>Квадрант</th></tr></thead>
<tbody>
<tr><td><strong style="color:#C9A84C;">SATORI (цель)</strong></td><td>Премиум (0.85)</td><td>Специализированный (0.9)</td><td style="color:#4A7C59;">✅ Свободная ниша</td></tr>
<tr><td>Pilates Реформер</td><td>Средний (0.55)</td><td>Специализированный (0.75)</td><td>Нишевые студии</td></tr>
<tr><td>Точка Баланса</td><td>Средний (0.45)</td><td>Специализированный (0.65)</td><td>Нишевые студии</td></tr>
<tr><td>Флекс</td><td>Бюджет (0.4)</td><td>Специализированный (0.6)</td><td>Нишевые студии</td></tr>
<tr><td>Level Wellness</td><td>Премиум (0.8)</td><td>Универсальный (0.3)</td><td>Премиум-клубы</td></tr>
<tr><td>King Fit</td><td>Премиум (0.7)</td><td>Универсальный (0.2)</td><td>Премиум-клубы</td></tr>
<tr><td>Олимп</td><td>Средний (0.5)</td><td>Универсальный (0.15)</td><td>Бюджетные залы</td></tr>
</tbody></table></div>
"""

FUNNEL_HTML = """
<div class="funnel">
<h4 style="text-align:center;color:#C9A84C;margin-bottom:15px;">🔄 Клиентская воронка SATORI</h4>
<div class="funnel-step" style="background:linear-gradient(135deg,#362A20,#2A1F17);border-left:4px solid #C44536;">👤 <strong>Новый клиент</strong> → Instagram / сарафанное радио</div>
<div class="funnel-arrow">⬇</div>
<div class="funnel-step" style="border-left:4px solid #C9A84C;">🏛️ <strong>SATORI Studio</strong> — Пробное занятие 500₽ → <em>80% конверсия в абонемент</em></div>
<div class="funnel-arrow">⬇</div>
<div class="funnel-step" style="border-left:4px solid #C9A84C;">📋 <strong>Абонемент</strong> 8 занятий = 8,000–10,000₽</div>
<div class="funnel-arrow">⬇</div>
<div class="funnel-step" style="border-left:4px solid #4A6FA5;">🧊 <strong>SATORI Cryo</strong> — Первый сеанс бесплатно → <em>50% покупают крио-абонемент (15,000₽)</em></div>
<div class="funnel-arrow">⬇</div>
<div class="funnel-step" style="border-left:4px solid #7b2cbf;">🔬 <strong>SATORI Bio</strong> — Бесплатный первый анализ → <em>40% подписываются (6,500₽/мес)</em></div>
<div class="funnel-arrow">⬇</div>
<div class="funnel-step" style="border-left:4px solid #4A7C59;">🧬 <strong>SATORI DNA</strong> — Разовый разбор 4,900₽ → подписка Pro 7,900₽/мес</div>
<div class="funnel-arrow">⬇</div>
<div class="funnel-step" style="background:linear-gradient(135deg,#6B4226,#362A20);border-left:4px solid #C9A84C;text-align:center;font-size:1.1em;">💰 <strong>Platinum-клиент = 35,000+₽/мес</strong></div>
</div>
"""

# Replace mermaid blocks
def fix_mermaid(m):
    content = m.group(1)
    if "quadrantChart" in content:
        return QUADRANT_HTML
    elif "graph TD" in content:
        return FUNNEL_HTML
    lines = [l.strip() for l in content.strip().split("\n") if l.strip() and not l.strip().startswith("style ")]
    formatted = "<br>".join(f"&nbsp;&nbsp;{l}" for l in lines)
    return f'<div class="mermaid-placeholder"><strong>📊 Диаграмма:</strong><br>{formatted}</div>'

md_text = re.sub(r'```mermaid\n(.*?)```', fix_mermaid, md_text, flags=re.DOTALL)

# === Alerts ===
def fix_alerts(m):
    alert_type = m.group(1).lower()
    content = m.group(2)
    content = re.sub(r'^>\s?', '', content, flags=re.MULTILINE).strip()
    content = content.replace("\n", "<br>")
    icon = {"tip": "💡", "important": "⚠️", "warning": "🔴", "note": "📝", "caution": "🚨"}.get(alert_type, "📌")
    return f'<div class="alert alert-{alert_type}">{icon} {content}</div>'

md_text = re.sub(r'>\s*\[!(TIP|IMPORTANT|WARNING|NOTE|CAUTION)\]\s*\n((?:>.*\n?)*)', fix_alerts, md_text, flags=re.IGNORECASE)

# === Convert ===
html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "nl2br"])

# === Inject page-breaks before h2 (except the first one) ===
h2_count = 0
def add_page_break(m):
    global h2_count
    h2_count += 1
    if h2_count > 1:
        return f'<div style="page-break-before:always;"></div>{m.group(0)}'
    return m.group(0)

html_body = re.sub(r'<h2>.*?</h2>', add_page_break, html_body)

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
:root{--bg:#1C1410;--bg2:#2A1F17;--card:#362A20;--gold:#C9A84C;--gold-light:#E8D48B;--gold-dark:#8B6914;--brown:#6B4226;--brown-light:#A0785C;--cream:#F5E6D3;--text:#E8DDD0;--muted:#A89888;}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);line-height:1.7;padding:50px 65px;font-size:13.5px;}
h1{font-family:'Playfair Display',serif;font-size:2.8em;font-weight:800;color:var(--gold);text-align:center;letter-spacing:3px;margin:20px 0 5px;text-transform:uppercase;}
h2{font-family:'Playfair Display',serif;font-size:1.5em;font-weight:700;color:var(--gold);margin:30px 0 16px;padding-bottom:8px;border-bottom:2px solid var(--brown);letter-spacing:1px;}
h3{font-size:1.1em;font-weight:600;color:var(--cream);margin:22px 0 10px;}
h4{font-size:0.95em;font-weight:600;color:var(--gold-light);margin:16px 0 8px;}
p{margin:6px 0;}
strong{color:var(--cream);}
em{color:var(--muted);font-style:italic;}
hr{border:none;height:2px;background:linear-gradient(90deg,transparent,var(--brown),var(--gold),var(--brown),transparent);margin:30px 0;}
blockquote{background:var(--bg2);border-left:4px solid var(--gold);padding:12px 18px;margin:12px 0;border-radius:0 8px 8px 0;font-style:italic;color:var(--muted);}
table{width:100%;border-collapse:collapse;margin:14px 0;font-size:0.85em;background:var(--bg2);overflow:hidden;box-shadow:0 3px 15px rgba(0,0,0,0.3);}
thead{background:linear-gradient(135deg,var(--brown),var(--card));}
th{color:var(--gold);padding:10px 12px;text-align:left;font-weight:600;font-size:0.85em;text-transform:uppercase;letter-spacing:0.5px;border-bottom:2px solid var(--gold-dark);}
td{padding:8px 12px;border-bottom:1px solid rgba(107,66,38,0.3);color:var(--text);}
tr:nth-child(even){background:rgba(201,168,76,0.03);}
pre,code{font-family:'Consolas','Courier New',monospace;font-size:0.82em;}
pre{background:var(--card);border:1px solid var(--brown);border-radius:8px;padding:16px;margin:12px 0;white-space:pre-wrap;color:var(--cream);page-break-inside:avoid;}
code{background:var(--card);padding:1px 5px;border-radius:3px;color:var(--gold-light);}
pre code{background:none;padding:0;}
ul,ol{margin:6px 0 6px 22px;}
li{margin:4px 0;color:var(--text);font-size:0.93em;}
li strong{color:var(--gold-light);}
img{display:block;max-width:90%;margin:12px auto;border:2px solid var(--brown);border-radius:10px;box-shadow:0 6px 25px rgba(0,0,0,0.5);}
.alert{padding:14px 18px;margin:14px 0;border-radius:8px;font-size:0.9em;line-height:1.5;page-break-inside:avoid;}
.alert-tip{background:rgba(74,124,89,0.15);border:1px solid #4A7C59;border-left:4px solid #4A7C59;}
.alert-important{background:rgba(201,168,76,0.1);border:1px solid var(--gold-dark);border-left:4px solid var(--gold);}
.alert-warning{background:rgba(196,69,54,0.1);border:1px solid #C44536;border-left:4px solid #C44536;}
.competitive-map{page-break-inside:avoid;margin:15px 0;}
.funnel{margin:15px 0;}
.funnel-step{background:var(--card);margin:6px 0;padding:10px 16px;border-radius:8px;font-size:0.9em;page-break-inside:avoid;}
.funnel-arrow{text-align:center;color:var(--gold);font-size:1.2em;margin:2px 0;}
h2,h3,h4{page-break-after:avoid;}
table{page-break-inside:avoid;}
@page{size:A4;margin:12mm 10mm;}
"""

full_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>SATORI Wellness Ecosystem — Стратегический анализ</title>
<style>{CSS}</style>
</head>
<body>
{html_body}
</body>
</html>"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(full_html)
print(f"✓ HTML saved: {HTML_PATH}")

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{HTML_PATH.replace(os.sep, '/')}")
    page.wait_for_timeout(5000)

    page.pdf(
        path=PDF_PATH,
        format="A4",
        margin={"top": "12mm", "bottom": "12mm", "left": "10mm", "right": "10mm"},
        print_background=True,
        prefer_css_page_size=False,
    )
    browser.close()

print(f"✓ PDF saved: {PDF_PATH}")
print(f"  Size: {os.path.getsize(PDF_PATH) / 1024 / 1024:.1f} MB")

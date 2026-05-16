"""OMI Brand Book — Luxury PDF Generator via Playwright"""
import base64
import os
import asyncio

IMG_DIR = r"C:\Users\Gigabyte\.gemini\antigravity\brain\c308ccc7-b5ab-4ee4-b74e-d1dc1a24403c"

def b64(name):
    path = os.path.join(IMG_DIR, name)
    if not os.path.exists(path):
        # find by prefix
        for f in os.listdir(IMG_DIR):
            if f.startswith(name.split('.')[0]) and f.endswith('.png'):
                path = os.path.join(IMG_DIR, f)
                break
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

imgs = {}
for prefix in ["omi_product_hero", "omi_nfc_tap_moment", "omi_moodboard", 
               "omi_lookbook_hoodie", "omi_ar_effect", "omi_packaging_unbox"]:
    for f in os.listdir(IMG_DIR):
        if f.startswith(prefix) and f.endswith('.png'):
            imgs[prefix] = b64(f)
            print(f"  ✓ {prefix}")
            break

HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Inter:wght@200;300;400;500&display=swap" rel="stylesheet">
<style>
@page {{ size: A4 landscape; margin: 0; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Inter',sans-serif; background:#0a0a0a; color:#e8e0d4; }}

.page {{
  width: 297mm; height: 210mm;
  page-break-after: always;
  position: relative; overflow: hidden;
  display: flex;
}}
.page:last-child {{ page-break-after: avoid; }}

/* === COVER === */
.cover {{
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1510 40%, #0d0b08 100%);
  justify-content: center; align-items: center; flex-direction: column;
  text-align: center;
}}
.cover::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(ellipse at 50% 50%, rgba(183,142,78,0.08) 0%, transparent 70%);
}}
.cover h1 {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 120px; font-weight: 300; letter-spacing: 30px;
  color: #b78e4e; position: relative; z-index: 1;
}}
.cover .sub {{
  font-size: 14px; letter-spacing: 8px; text-transform: uppercase;
  color: rgba(183,142,78,0.6); margin-top: 20px; position: relative; z-index: 1;
}}
.cover .tagline {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 22px; font-style: italic; font-weight: 300;
  color: rgba(232,224,212,0.5); margin-top: 40px; position: relative; z-index: 1;
}}
.cover .line {{
  width: 80px; height: 1px; background: #b78e4e; margin: 30px auto; opacity: 0.4;
  position: relative; z-index: 1;
}}
.cover .year {{
  font-size: 11px; letter-spacing: 6px; color: rgba(183,142,78,0.3);
  position: absolute; bottom: 30px; z-index: 1;
}}

/* === SPLIT PAGE === */
.split {{ display: flex; }}
.split .img-half {{
  width: 50%; height: 210mm;
  background-size: cover; background-position: center;
}}
.split .text-half {{
  width: 50%; height: 210mm; padding: 50px 45px;
  display: flex; flex-direction: column; justify-content: center;
  background: #0d0b08;
}}

/* === FULL IMAGE PAGE === */
.full-img {{
  background-size: cover; background-position: center;
  position: relative;
}}
.full-img .overlay {{
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 50px; background: linear-gradient(transparent, rgba(10,10,10,0.95));
}}

/* === TEXT STYLES === */
.section-label {{
  font-size: 10px; letter-spacing: 5px; text-transform: uppercase;
  color: #b78e4e; margin-bottom: 20px; opacity: 0.7;
}}
h2 {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 42px; font-weight: 300; color: #e8e0d4;
  line-height: 1.2; margin-bottom: 25px;
}}
h3 {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 28px; font-weight: 400; color: #b78e4e;
  margin-bottom: 15px;
}}
p {{ font-size: 13px; line-height: 1.9; color: rgba(232,224,212,0.7); margin-bottom: 15px; font-weight: 300; }}
.accent {{ color: #b78e4e; }}
.quote {{
  font-family: 'Cormorant Garamond', serif;
  font-size: 26px; font-style: italic; font-weight: 300;
  color: rgba(183,142,78,0.8); line-height: 1.5;
  border-left: 2px solid rgba(183,142,78,0.3); padding-left: 25px;
  margin: 20px 0;
}}

/* === GRID PAGE === */
.grid-page {{ flex-direction: column; background: #0d0b08; padding: 50px; }}
.grid-page .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 30px; flex: 1; }}
.grid-page .grid .card {{
  background: rgba(183,142,78,0.04); border: 1px solid rgba(183,142,78,0.1);
  border-radius: 4px; padding: 30px; display: flex; flex-direction: column;
}}
.card .price {{ font-family: 'Cormorant Garamond', serif; font-size: 36px; color: #b78e4e; margin: 10px 0; }}
.card .tier {{ font-size: 10px; letter-spacing: 4px; text-transform: uppercase; color: #b78e4e; }}
.card ul {{ list-style: none; margin-top: 15px; }}
.card ul li {{ font-size: 11px; color: rgba(232,224,212,0.6); padding: 5px 0; border-bottom: 1px solid rgba(183,142,78,0.06); }}
.card ul li::before {{ content: '—  '; color: #b78e4e; }}

/* === COLOR PAGE === */
.colors-row {{ display: flex; gap: 20px; margin: 20px 0; }}
.color-swatch {{
  width: 80px; height: 80px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 9px; letter-spacing: 1px; text-align: center;
}}

/* === TWO COL TEXT === */
.two-col {{ display: flex; gap: 50px; }}
.two-col .col {{ flex: 1; }}

/* === FOOTER === */
.page-num {{
  position: absolute; bottom: 20px; right: 30px;
  font-size: 9px; letter-spacing: 3px; color: rgba(183,142,78,0.3);
}}

/* NFC FLOW */
.flow {{ display: flex; align-items: center; gap: 15px; margin: 12px 0; }}
.flow .step {{
  background: rgba(183,142,78,0.08); border: 1px solid rgba(183,142,78,0.15);
  border-radius: 4px; padding: 12px 18px; font-size: 11px; color: #b78e4e;
  text-align: center; min-width: 100px;
}}
.flow .arrow {{ color: rgba(183,142,78,0.3); font-size: 18px; }}
</style></head><body>

<!-- PAGE 1: COVER -->
<div class="page cover">
  <div class="line"></div>
  <h1>OMI</h1>
  <div class="sub">Brand Book 2026</div>
  <div class="tagline">Носи свой миф</div>
  <div class="line"></div>
  <div class="year">WEAR YOUR MYTH — BRAND IDENTITY GUIDELINES</div>
</div>

<!-- PAGE 2: ORIGIN STORY -->
<div class="page split">
  <div class="img-half" style="background-image:url('{imgs.get("omi_moodboard","")}')"></div>
  <div class="text-half">
    <div class="section-label">01 — Происхождение</div>
    <h2>История,<br>ставшая брендом</h2>
    <p>Название OMI связано с человеком по имени Омар, которого близкие звали Оми. Он ушёл рано, но оставил ощущение ценности прожитой жизни, уважения к времени, к труду, к красоте, созданной руками и наполненной смыслом.</p>
    <p>Он был связан с мёдом, с ремеслом, с тихим искусством превращать собранный нектар во что-то драгоценное. Эта метафора стала основой бренда.</p>
    <div class="quote">«Так же как пчела собирает нектар с разных цветов и превращает его в мёд, OMI собирает образы, символы, мифы и личные воспоминания, чтобы воплотить их в одежде.»</div>
    <span class="page-num">02</span>
  </div>
</div>

<!-- PAGE 3: MISSION & PHILOSOPHY -->
<div class="page split">
  <div class="text-half" style="padding: 50px 45px;">
    <div class="section-label">02 — Миссия и философия</div>
    <h2>Сохранять память через красоту</h2>
    <p><strong class="accent">Миссия:</strong> Сохранять память и передавать смыслы через красоту, к которой можно прикоснуться.</p>
    <p><strong class="accent">Видение:</strong> Стать брендом, формирующим новую категорию осмысленной моды, где вещь ценится не только за внешний эффект, но и за глубину, историю и интеллектуальную эстетику.</p>
    <h3 style="margin-top:25px;">Ценности</h3>
    <div class="two-col" style="margin-top:10px;">
      <div class="col">
        <p>◆ <span class="accent">Память</span> — фундамент каждой вещи</p>
        <p>◆ <span class="accent">Красота</span> — форма высказывания</p>
        <p>◆ <span class="accent">Глубина</span> — содержание за эстетикой</p>
      </div>
      <div class="col">
        <p>◆ <span class="accent">Культурный код</span> — язык символов</p>
        <p>◆ <span class="accent">Индивидуальность</span> — не массовое</p>
        <p>◆ <span class="accent">Переосмысление</span> — не копия прошлого</p>
      </div>
    </div>
    <span class="page-num">03</span>
  </div>
  <div class="img-half" style="background-image:url('{imgs.get("omi_lookbook_hoodie","")}')"></div>
</div>

<!-- PAGE 4: VISUAL IDENTITY -->
<div class="page grid-page">
  <div class="section-label">03 — Визуальная идентичность</div>
  <h2 style="margin-bottom:30px;">Цвета, типографика, настроение</h2>
  <div style="display:flex; gap:40px; flex:1;">
    <div style="flex:1;">
      <h3>Цветовая палитра</h3>
      <div class="colors-row">
        <div>
          <div class="color-swatch" style="background:#0a0a0a; border:1px solid rgba(183,142,78,0.2); color:rgba(232,224,212,0.5);">Obsidian</div>
          <p style="font-size:9px; text-align:center; margin-top:6px;">#0A0A0A</p>
        </div>
        <div>
          <div class="color-swatch" style="background:#b78e4e; color:#0a0a0a;">Amber<br>Gold</div>
          <p style="font-size:9px; text-align:center; margin-top:6px;">#B78E4E</p>
        </div>
        <div>
          <div class="color-swatch" style="background:#e8e0d4; color:#0a0a0a;">Bone</div>
          <p style="font-size:9px; text-align:center; margin-top:6px;">#E8E0D4</p>
        </div>
        <div>
          <div class="color-swatch" style="background:#1a1510; border:1px solid rgba(183,142,78,0.2); color:rgba(232,224,212,0.5);">Dark<br>Honey</div>
          <p style="font-size:9px; text-align:center; margin-top:6px;">#1A1510</p>
        </div>
      </div>
      <h3 style="margin-top:25px;">Типографика</h3>
      <p style="font-family:'Cormorant Garamond',serif; font-size:32px; font-weight:300; color:#e8e0d4;">Cormorant Garamond</p>
      <p style="font-size:10px; color:rgba(232,224,212,0.4); margin-top:5px;">Заголовки, слоганы, цитаты — поэтичность и элегантность</p>
      <p style="font-family:'Inter',sans-serif; font-size:16px; font-weight:200; color:#e8e0d4; margin-top:15px;">Inter — Light / Regular</p>
      <p style="font-size:10px; color:rgba(232,224,212,0.4); margin-top:5px;">Тело текста, UI, навигация — чистота и читаемость</p>
    </div>
    <div style="flex:1;">
      <h3>Tone of Voice</h3>
      <p>Поэтично, но собранно.<br>Глубоко, но не вычурно.<br>Интеллектуально, но не академично.<br>Эмоционально, но без пафоса.<br>Красиво, но точно.</p>
      <h3 style="margin-top:20px;">Архетип бренда</h3>
      <p><span class="accent" style="font-size:18px;">Творец</span> — основной<br>
      <span class="accent" style="font-size:18px;">Мудрец</span> — вторичный<br>
      <span class="accent" style="font-size:14px;">Хранитель</span> — оттенок</p>
      <h3 style="margin-top:20px;">Ключевые фразы</h3>
      <p>◆ OMI — носи свой миф<br>◆ Wear your myth<br>◆ Одежда, в которой живёт память<br>◆ Прикоснись к истории<br>◆ Красота со смыслом</p>
    </div>
  </div>
  <span class="page-num">04</span>
</div>

<!-- PAGE 5: PRODUCT HERO -->
<div class="page full-img" style="background-image:url('{imgs.get("omi_product_hero","")}')">
  <div class="overlay">
    <div class="section-label">04 — Продукт</div>
    <h2>Не одежда. Артефакт.</h2>
    <p style="max-width:500px;">Каждая вещь OMI создаётся как артефакт: в ней красота соединяется со смыслом, а декор становится языком. Орнаменты, вышивка, фактуры — визуальный рассказ, зашифрованный в ткани.</p>
  </div>
  <span class="page-num" style="color:rgba(255,255,255,0.3);">05</span>
</div>

<!-- PAGE 6: PRODUCT LINES -->
<div class="page grid-page">
  <div class="section-label">04 — Линейка продуктов</div>
  <h2 style="margin-bottom:20px;">Три уровня мифа</h2>
  <div class="grid" style="flex:1;">
    <div class="card">
      <div class="tier">🐝 Core</div>
      <div style="font-family:'Cormorant Garamond',serif; font-size:20px; color:#e8e0d4; margin-top:5px;">Everyday Myth</div>
      <div class="price">$90</div>
      <ul>
        <li>Футболки и лонгсливы</li>
        <li>Один ключевой символ</li>
        <li>100% органический хлопок, 220 gsm</li>
        <li>NFC: сертификат + история + плейлист</li>
        <li>Тираж: 200 шт / символ</li>
        <li>Себестоимость: $19.5</li>
        <li>Маржа: 78%</li>
      </ul>
    </div>
    <div class="card" style="border-color:rgba(183,142,78,0.25); background:rgba(183,142,78,0.06);">
      <div class="tier">🏛️ Artifact</div>
      <div style="font-family:'Cormorant Garamond',serif; font-size:20px; color:#e8e0d4; margin-top:5px;">Wearable Legend</div>
      <div class="price">$135</div>
      <ul>
        <li>Худи и куртки-бомберы</li>
        <li>Сложная декоративная вышивка</li>
        <li>Premium fleece / Japanese cotton</li>
        <li>NFC: AR-эффект + видео + community</li>
        <li>Тираж: 100 шт / дроп</li>
        <li>Себестоимость: $38</li>
        <li>Маржа: 72%</li>
      </ul>
    </div>
    <div class="card">
      <div class="tier">👑 Relic</div>
      <div style="font-family:'Cormorant Garamond',serif; font-size:20px; color:#e8e0d4; margin-top:5px;">One of Few</div>
      <div class="price">$250</div>
      <ul>
        <li>Коллаборационные капсулы</li>
        <li>Handcrafted уникальный декор</li>
        <li>Premium fabrics</li>
        <li>NFC: полный пакет + NFT-двойник</li>
        <li>Тираж: 50 шт / коллаб</li>
        <li>Себестоимость: $73.5</li>
        <li>Маржа: 71%</li>
      </ul>
    </div>
  </div>
  <span class="page-num">06</span>
</div>

<!-- PAGE 7: NFC EXPERIENCE -->
<div class="page split">
  <div class="img-half" style="background-image:url('{imgs.get("omi_nfc_tap_moment","")}')"></div>
  <div class="text-half">
    <div class="section-label">05 — NFC Experience</div>
    <h2>Прикоснись<br>к истории</h2>
    <p>Каждая вещь OMI содержит вшитый NFC-чип NXP NTAG 424 DNA с криптографической защитой. Приложите телефон — и миф оживает.</p>
    <div class="flow">
      <div class="step">📱 TAP</div>
      <div class="arrow">→</div>
      <div class="step">🔐 Аутентификация</div>
      <div class="arrow">→</div>
      <div class="step">📖 Цифровой миф</div>
    </div>
    <p style="margin-top:15px;"><span class="accent">Сертификат:</span> #047/200 — серийный номер, дата, blockchain</p>
    <p><span class="accent">История:</span> Миф, вдохновивший дизайн + видео создания</p>
    <p><span class="accent">AR-эффект:</span> Орнамент оживает через камеру</p>
    <p><span class="accent">Плейлист:</span> Курированный саундтрек коллекции</p>
    <p><span class="accent">Community:</span> OMI Hive — ранний доступ к дропам</p>
    <span class="page-num">07</span>
  </div>
</div>

<!-- PAGE 8: AR -->
<div class="page full-img" style="background-image:url('{imgs.get("omi_ar_effect","")}')">
  <div class="overlay">
    <div class="section-label">06 — Augmented Reality</div>
    <h2>Миф оживает<br>при касании</h2>
    <p style="max-width:500px;">WebAR без установки приложений. Наведите камеру на орнамент — и древние символы обретают жизнь. Анимация поверх ткани, Instagram-фильтр, shareable контент. Технология 8th Wall.</p>
  </div>
  <span class="page-num" style="color:rgba(255,255,255,0.3);">08</span>
</div>

<!-- PAGE 9: PACKAGING -->
<div class="page split">
  <div class="text-half">
    <div class="section-label">07 — Упаковка</div>
    <h2>Unboxing<br>как ритуал</h2>
    <p>Каждая вещь OMI приходит в premium-боксе из матового картона с тиснением золотого логотипа. Внутри: тканевая бумага с фирменным паттерном, карточка с историей вещи, буклет бренда.</p>
    <div class="quote" style="font-size:20px;">«Спасибо, что выбрали вещь со смыслом. Пусть эта вещь станет частью вашего собственного мифа.»</div>
    <p><span class="accent">Вкладыш:</span> «Приложи телефон к бирке — узнай историю этой вещи»</p>
    <p><span class="accent">Бирка:</span> «Одежда как носитель памяти, мифа и культурного кода»</p>
    <span class="page-num">09</span>
  </div>
  <div class="img-half" style="background-image:url('{imgs.get("omi_packaging_unbox","")}')"></div>
</div>

<!-- PAGE 10: MANIFESTO -->
<div class="page cover" style="background: linear-gradient(135deg, #0d0b08 0%, #1a1510 50%, #0a0a0a 100%);">
  <div class="line"></div>
  <div style="max-width:600px; position:relative; z-index:1; text-align:center;">
    <div class="section-label" style="margin-bottom:30px;">Манифест</div>
    <div class="quote" style="border:none; padding:0; text-align:center; font-size:22px; line-height:1.8;">
      Мы верим, что человек состоит из историй.<br>
      Из памяти семьи. Из образов, которые он унаследовал.<br>
      Из мифов, которые однажды узнал и сохранил внутри.<br><br>
      Мы создаём одежду не как случайный предмет,<br>
      а как продолжение этой внутренней истории.<br><br>
      Мы не копируем прошлое. Мы переосмысляем его.<br>
      Мы собираем его фрагменты — как пчела собирает нектар —<br>
      и превращаем в новый язык.
    </div>
    <div style="margin-top:40px; font-family:'Cormorant Garamond',serif; font-size:48px; color:#b78e4e; font-weight:300;">OMI</div>
    <div style="font-size:12px; letter-spacing:6px; color:rgba(183,142,78,0.5); margin-top:10px;">НОСИ СВОЙ МИФ</div>
  </div>
  <div class="line"></div>
  <div class="year">© OMI 2026 — ALL RIGHTS RESERVED</div>
</div>

</body></html>"""

async def render():
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        await page.set_content(HTML, wait_until="networkidle")
        await page.wait_for_timeout(2000)
        out = r"c:\Dev\METAai\OMI_BRAND_BOOK.pdf"
        await page.pdf(
            path=out,
            format="A4",
            landscape=True,
            print_background=True,
            margin={"top":"0","right":"0","bottom":"0","left":"0"}
        )
        await browser.close()
        print(f"✓ Brand Book saved: {out}")
        print(f"  Size: {os.path.getsize(out)/1024:.0f} KB")

asyncio.run(render())

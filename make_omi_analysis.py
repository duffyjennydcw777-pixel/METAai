"""OMI Strategic Analysis — Luxury PDF"""
import base64
import os
import asyncio

IMG_DIR = r"C:\Users\Gigabyte\.gemini\antigravity\brain\c308ccc7-b5ab-4ee4-b74e-d1dc1a24403c"
imgs = {}
for prefix in ["omi_product_hero", "omi_moodboard"]:
    for f in os.listdir(IMG_DIR):
        if f.startswith(prefix) and f.endswith('.png'):
            with open(os.path.join(IMG_DIR, f), "rb") as fh:
                imgs[prefix] = "data:image/png;base64," + base64.b64encode(fh.read()).decode()
            break

CSS = """
@page { size: A4; margin: 0; }
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Inter',sans-serif; background:#0a0a0a; color:#e8e0d4; }
.pg { width:210mm; min-height:297mm; padding:40px 45px; page-break-after:always; position:relative; background:#0d0b08; }
.pg:last-child { page-break-after:avoid; }
.cover { display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;
  background: linear-gradient(135deg,#0a0a0a,#1a1510 50%,#0d0b08); }
.cover h1 { font-family:'Cormorant Garamond',serif; font-size:96px; font-weight:300; letter-spacing:20px; color:#b78e4e; }
.lbl { font-size:9px; letter-spacing:5px; text-transform:uppercase; color:#b78e4e; opacity:.7; margin-bottom:18px; }
h2 { font-family:'Cormorant Garamond',serif; font-size:32px; font-weight:300; color:#e8e0d4; margin-bottom:20px; line-height:1.3; }
h3 { font-family:'Cormorant Garamond',serif; font-size:20px; color:#b78e4e; margin:18px 0 10px; }
p { font-size:11.5px; line-height:1.8; color:rgba(232,224,212,.7); font-weight:300; margin-bottom:10px; }
.a { color:#b78e4e; }
table { width:100%; border-collapse:collapse; margin:12px 0; font-size:10.5px; }
th { background:rgba(183,142,78,.1); color:#b78e4e; text-align:left; padding:8px 10px; font-weight:400; letter-spacing:1px; font-size:9px; text-transform:uppercase; }
td { padding:7px 10px; border-bottom:1px solid rgba(183,142,78,.06); color:rgba(232,224,212,.65); }
tr:hover td { background:rgba(183,142,78,.03); }
.num { position:absolute; bottom:18px; right:25px; font-size:8px; letter-spacing:3px; color:rgba(183,142,78,.25); }
.line { width:60px; height:1px; background:#b78e4e; margin:20px auto; opacity:.3; }
.sub { font-size:12px; letter-spacing:6px; color:rgba(183,142,78,.5); margin-top:12px; }
ul { list-style:none; margin:8px 0; }
ul li { font-size:11px; color:rgba(232,224,212,.6); padding:4px 0; }
ul li::before { content:'— '; color:#b78e4e; }
.q { font-family:'Cormorant Garamond',serif; font-size:20px; font-style:italic; color:rgba(183,142,78,.7); border-left:2px solid rgba(183,142,78,.25); padding-left:20px; margin:15px 0; line-height:1.6; }
.row { display:flex; gap:30px; }
.col { flex:1; }
.kpi { text-align:center; padding:15px; background:rgba(183,142,78,.04); border:1px solid rgba(183,142,78,.1); border-radius:4px; }
.kpi .v { font-family:'Cormorant Garamond',serif; font-size:36px; color:#b78e4e; }
.kpi .k { font-size:9px; letter-spacing:2px; color:rgba(232,224,212,.4); margin-top:4px; text-transform:uppercase; }
"""

HTML = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300&family=Inter:wght@200;300;400;500&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>

<div class="pg cover">
  <div class="line"></div>
  <h1>OMI</h1>
  <div class="sub">STRATEGIC ANALYSIS</div>
  <p style="color:rgba(183,142,78,.4); margin-top:30px; font-size:13px; font-style:italic;">NFC-Enabled Fashion Brand</p>
  <p style="color:rgba(183,142,78,.3); font-size:10px; letter-spacing:3px; margin-top:8px;">БИЗНЕС-МОДЕЛЬ • ФИНАНСЫ • GTM • ROADMAP</p>
  <div class="line"></div>
  <p style="position:absolute;bottom:25px;font-size:9px;letter-spacing:4px;color:rgba(183,142,78,.2);">CONFIDENTIAL — 2026</p>
</div>

<!-- EXEC SUMMARY -->
<div class="pg">
  <div class="lbl">01 — Executive Summary</div>
  <h2>OMI — одежда как wearable-платформа</h2>
  <p>OMI объединяет эмоциональную глубину авторского fashion-бренда с технологией NFC-чипирования. Каждая вещь содержит криптографически защищённый чип, превращающий одежду в интерактивный цифровой артефакт.</p>

  <div class="row" style="margin:25px 0;">
    <div class="kpi"><div class="v">$288K</div><div class="k">Revenue Year 1</div></div>
    <div class="kpi"><div class="v">$148K</div><div class="k">EBITDA Year 1</div></div>
    <div class="kpi"><div class="v">2,700</div><div class="k">Единиц Year 1</div></div>
    <div class="kpi"><div class="v">74%</div><div class="k">Средняя маржа</div></div>
  </div>

  <h3>Ключевое отличие</h3>
  <p>Для масс-маркета NFC — это верификация подлинности. Для OMI — <span class="a">портал в миф</span>. Чип рассказывает историю вещи, запускает AR-анимацию, открывает community и подтверждает уникальность (#047/200).</p>

  <h3>Бизнес-модель</h3>
  <p>Drop-модель: лимитированные серии по 50–200 штук. Три линейки: <span class="a">Core</span> ($90, футболки), <span class="a">Artifact</span> ($135, худи), <span class="a">Relic</span> ($250, коллабы). Производство: Турция (MOQ от 50 шт, Aegean cotton, логистика 5-7 дней).</p>

  <h3>Целевая аудитория</h3>
  <p>Эстетически чувствительный городской человек 25–40 лет. Устал от безликого масс-маркета. Ценит индивидуальность, культурный вкус, символизм. Покупает не одежду — покупает <span class="a">чувство уникальности и интеллектуальную красоту</span>.</p>
  <div class="num">02</div>
</div>

<!-- MARKET -->
<div class="pg">
  <div class="lbl">02 — Рыночный анализ</div>
  <h2>Рынок и конкурентное позиционирование</h2>

  <h3>Размер рынка</h3>
  <table>
    <tr><th>Сегмент</th><th>Глобальный объём</th><th>Рост CAGR</th><th>Релевантность</th></tr>
    <tr><td>Streetwear</td><td>$187B (2025)</td><td>10.3%</td><td>Основной рынок</td></tr>
    <tr><td>NFC/Smart Fashion</td><td>$4.2B (2025)</td><td>22.8%</td><td>Технологическая ниша</td></tr>
    <tr><td>Conscious/Slow Fashion</td><td>$8.1B (2025)</td><td>9.1%</td><td>Ценностная ниша</td></tr>
    <tr><td>Limited Edition/Drop</td><td>$12B (2025)</td><td>15.4%</td><td>Бизнес-модель</td></tr>
  </table>

  <h3>Конкурентная карта</h3>
  <table>
    <tr><th>Бренд</th><th>Цена</th><th>NFC</th><th>Культурный код</th><th>Drop-модель</th><th>Отличие OMI</th></tr>
    <tr><td>Supreme</td><td>$40-300</td><td>Нет</td><td>Субкультура</td><td>Да</td><td>Глубина vs. хайп</td></tr>
    <tr><td>Story mfg.</td><td>$150-500</td><td>Нет</td><td>Ремесло</td><td>Нет</td><td>NFC-слой</td></tr>
    <tr><td>Bode</td><td>$200-800</td><td>Нет</td><td>Винтаж/арт</td><td>Нет</td><td>Доступнее + tech</td></tr>
    <tr><td>MNTGE</td><td>$150-400</td><td>Да (NFT)</td><td>Нет</td><td>Да</td><td>Смысл vs. спекуляция</td></tr>
    <tr><td>Visvim</td><td>$300-1500</td><td>Нет</td><td>Японское ремесло</td><td>Нет</td><td>Доступнее + tech</td></tr>
  </table>

  <div class="q">«Многие бренды используют эстетику как форму впечатления. OMI использует эстетику как форму повествования.»</div>

  <h3>Свободная ниша</h3>
  <p>Ни один бренд не объединяет: (1) глубокий культурный нарратив, (2) NFC-интерактивность, (3) AR-визуализацию, (4) drop-модель с доказуемой лимитированностью. OMI занимает пересечение этих четырёх осей.</p>
  <div class="num">03</div>
</div>

<!-- FINANCIAL MODEL -->
<div class="pg">
  <div class="lbl">03 — Финансовая модель</div>
  <h2>P&L прогноз: Year 1</h2>

  <h3>Себестоимость по линейкам</h3>
  <table>
    <tr><th>Компонент</th><th>Core ($90)</th><th>Artifact ($135)</th><th>Relic ($250)</th></tr>
    <tr><td>Ткань + пошив (Турция)</td><td>$12</td><td>$22</td><td>$40</td></tr>
    <tr><td>NFC-чип NTAG 424 DNA</td><td>$1.5</td><td>$1.5</td><td>$1.5</td></tr>
    <tr><td>Вышивка / декор</td><td>$2</td><td>$8</td><td>$20</td></tr>
    <tr><td>Упаковка (premium box)</td><td>$3</td><td>$5</td><td>$10</td></tr>
    <tr><td>Бирка + карточка</td><td>$1</td><td>$1.5</td><td>$2</td></tr>
    <tr><td style="color:#b78e4e;font-weight:500;">Себестоимость</td><td style="color:#b78e4e;">$19.5</td><td style="color:#b78e4e;">$38</td><td style="color:#b78e4e;">$73.5</td></tr>
    <tr><td style="color:#b78e4e;font-weight:500;">Маржа</td><td style="color:#b78e4e;">78%</td><td style="color:#b78e4e;">72%</td><td style="color:#b78e4e;">71%</td></tr>
  </table>

  <h3>Квартальный прогноз</h3>
  <table>
    <tr><th>Квартал</th><th>Дропы</th><th>Единиц</th><th>Avg Price</th><th>Revenue</th><th>COGS</th><th>Gross Profit</th></tr>
    <tr><td>Q1</td><td>Core ×3</td><td>600</td><td>$90</td><td>$54,000</td><td>$11,700</td><td>$42,300</td></tr>
    <tr><td>Q2</td><td>Core ×2 + Artifact ×2</td><td>600</td><td>$110</td><td>$66,000</td><td>$17,200</td><td>$48,800</td></tr>
    <tr><td>Q3</td><td>Core ×2 + Art ×2 + Relic ×1</td><td>650</td><td>$115</td><td>$74,750</td><td>$20,800</td><td>$53,950</td></tr>
    <tr><td>Q4</td><td>Core ×3 + Art ×2 + Relic ×1</td><td>850</td><td>$110</td><td>$93,500</td><td>$26,100</td><td>$67,400</td></tr>
    <tr><td style="color:#b78e4e;font-weight:500;">ИТОГО Y1</td><td></td><td style="color:#b78e4e;">2,700</td><td></td><td style="color:#b78e4e;">$288,250</td><td style="color:#b78e4e;">$75,800</td><td style="color:#b78e4e;">$212,450</td></tr>
  </table>

  <h3>Операционные расходы Year 1</h3>
  <div class="row">
    <div class="col">
      <table>
        <tr><th>Статья</th><th>Сумма</th></tr>
        <tr><td>Разработка PWA + AR</td><td>$8,000</td></tr>
        <tr><td>NFC-платформа (SaaS)</td><td>$2,400</td></tr>
        <tr><td>Фото/видео контент</td><td>$6,000</td></tr>
        <tr><td>Маркетинг (TikTok + influencers)</td><td>$24,000</td></tr>
      </table>
    </div>
    <div class="col">
      <table>
        <tr><th>Статья</th><th>Сумма</th></tr>
        <tr><td>Логистика overhead</td><td>$12,000</td></tr>
        <tr><td>Операционные (Shopify, инфра)</td><td>$3,600</td></tr>
        <tr><td>Pop-up events (×2)</td><td>$8,000</td></tr>
        <tr><td style="color:#b78e4e;">ИТОГО OPEX</td><td style="color:#b78e4e;">$64,000</td></tr>
      </table>
    </div>
  </div>
  <div class="row" style="margin-top:20px;">
    <div class="kpi"><div class="v">$212K</div><div class="k">Gross Profit</div></div>
    <div class="kpi"><div class="v">$64K</div><div class="k">OPEX</div></div>
    <div class="kpi"><div class="v" style="font-size:42px;">$148K</div><div class="k">EBITDA Year 1</div></div>
  </div>
  <div class="num">04</div>
</div>

<!-- GTM + ROADMAP -->
<div class="pg">
  <div class="lbl">04 — Go-To-Market & Roadmap</div>
  <h2>Стратегия запуска</h2>

  <div class="row">
    <div class="col">
      <h3>Фаза 1: «Шёпот» (мес. 1-2)</h3>
      <ul>
        <li>9 тизерных постов в Instagram</li>
        <li>Символика без объяснений — интрига</li>
        <li>20 вещей Core → блогерам/стилистам</li>
        <li>3 TikTok: «что если приложить телефон?»</li>
      </ul>
      <h3>Фаза 2: «Первый дроп» (мес. 3)</h3>
      <ul>
        <li>600 вещей Core (3 символа × 200)</li>
        <li>Shopify + кастомная NFC-страница</li>
        <li>Target revenue: $54,000</li>
        <li>Анонс линейки Artifact</li>
      </ul>
    </div>
    <div class="col">
      <h3>Фаза 3: «Углубление» (мес. 4-6)</h3>
      <ul>
        <li>200 вещей Artifact (2 дизайна)</li>
        <li>Первая коллаб → Relic (50 шт)</li>
        <li>Запуск OMI Hive community</li>
        <li>Pop-up Москва / Дубай (invite-only)</li>
      </ul>
      <h3>Фаза 4: «Масштаб» (мес. 7-12)</h3>
      <ul>
        <li>Дропы каждые 6 недель</li>
        <li>TikTok creator program (10 creators)</li>
        <li>Коллаб с поэтом/писателем</li>
        <li>Выход на international (Европа, GCC)</li>
      </ul>
    </div>
  </div>

  <h3 style="margin-top:25px;">Производственная цепочка</h3>
  <table>
    <tr><th>Этап</th><th>Локация</th><th>Детали</th></tr>
    <tr><td>Дизайн</td><td>OMI Studio</td><td>Авторские принты, символы, орнаменты</td></tr>
    <tr><td>Ткань</td><td>Denizli, Турция</td><td>Aegean cotton, premium fleece</td></tr>
    <tr><td>Пошив</td><td>Istanbul, Турция</td><td>MOQ 50-100 шт, малые фабрики</td></tr>
    <tr><td>Декор</td><td>Турция / локально</td><td>Машинная + ручная вышивка (Relic)</td></tr>
    <tr><td>NFC</td><td>In-house</td><td>Batch-программирование, 5 мин / 100 чипов</td></tr>
    <tr><td>Упаковка</td><td>Локально</td><td>Матовый бокс, тиснение, tissue paper</td></tr>
    <tr><td>Доставка</td><td>CDEK / DHL</td><td>РФ 2-5 дней, international 5-10 дней</td></tr>
  </table>

  <h3>Технический стек NFC</h3>
  <p><span class="a">Чип:</span> NXP NTAG 424 DNA — криптографическая аутентификация, невозможно клонировать, $0.80-1.50/шт.<br>
  <span class="a">PWA:</span> Supabase + Vercel — tap.omi-brand.com/{{chip-id}}.<br>
  <span class="a">AR:</span> 8th Wall WebAR — без установки приложений.<br>
  <span class="a">Стирка:</span> Чип выдерживает до 60°C, не повреждается при глажке.</p>
  <div class="num">05</div>
</div>

<!-- NEXT STEPS -->
<div class="pg cover" style="background:linear-gradient(135deg,#0d0b08,#1a1510 50%,#0a0a0a);">
  <div class="line"></div>
  <div style="max-width:500px;position:relative;z-index:1;text-align:center;">
    <div class="lbl" style="margin-bottom:25px;">Immediate Next Steps</div>
    <ul style="text-align:left;">
      <li>Утвердить 3 символа для первого дропа Core</li>
      <li>Найти фабрику в Турции (Istanbul/Denizli, MOQ 50)</li>
      <li>Заказать тестовые NTAG 424 DNA (100 шт, ~$120)</li>
      <li>Разработать PWA-прототип (tap → landing)</li>
      <li>Мудборд + фотосессия первой коллекции</li>
      <li>Домен omi-brand.com / wearomi.com</li>
      <li>Instagram @omi.myth / @wearomi</li>
      <li>9 стартовых публикаций</li>
    </ul>
    <div style="margin-top:40px;font-family:'Cormorant Garamond',serif;font-size:48px;color:#b78e4e;">OMI</div>
    <div style="font-size:11px;letter-spacing:5px;color:rgba(183,142,78,.4);margin-top:8px;">WEAR YOUR MYTH</div>
  </div>
  <div class="line"></div>
  <p style="position:absolute;bottom:20px;font-size:8px;letter-spacing:4px;color:rgba(183,142,78,.15);">© OMI 2026 — CONFIDENTIAL</p>
</div>

</body></html>"""

async def render():
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        await page.set_content(HTML, wait_until="networkidle")
        await page.wait_for_timeout(1500)
        out = r"c:\Dev\METAai\OMI_STRATEGIC_ANALYSIS.pdf"
        await page.pdf(path=out, format="A4", print_background=True,
                       margin={"top":"0","right":"0","bottom":"0","left":"0"})
        await browser.close()
        print(f"✓ Analysis saved: {out} ({os.path.getsize(out)/1024:.0f} KB)")

asyncio.run(render())

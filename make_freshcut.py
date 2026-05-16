"""FreshCut Greens Business Plan — Luxury PDF"""
import base64
import os
import asyncio
IMG = r"C:\Users\Gigabyte\.gemini\antigravity\brain\c308ccc7-b5ab-4ee4-b74e-d1dc1a24403c"
def b(prefix):
    for f in os.listdir(IMG):
        if f.startswith(prefix) and f.endswith('.png'):
            with open(os.path.join(IMG,f),"rb") as fh:
                return "data:image/png;base64,"+base64.b64encode(fh.read()).decode()
    return ""
i={}
for p in["freshcut_greenhouse","freshcut_product_packaging","freshcut_brand_logo","freshcut_restaurant_plate"]:
    i[p]=b(p); print(f"  ✓ {p}")
CSS="""@page{size:A4;margin:0}*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;background:#0a120a;color:#e0e8e0}
.pg{width:210mm;min-height:297mm;padding:40px 45px;page-break-after:always;position:relative;background:#0c1a0c}
.pg:last-child{page-break-after:avoid}
.cover{display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;background:linear-gradient(135deg,#0a120a,#1a2e1a 50%,#0c1a0c)}
.cover h1{font-family:'Cormorant Garamond',serif;font-size:72px;font-weight:300;letter-spacing:12px;color:#5cb85c}
.lbl{font-size:9px;letter-spacing:5px;text-transform:uppercase;color:#5cb85c;opacity:.7;margin-bottom:18px}
h2{font-family:'Cormorant Garamond',serif;font-size:30px;font-weight:300;color:#e0e8e0;margin-bottom:18px;line-height:1.3}
h3{font-family:'Cormorant Garamond',serif;font-size:18px;color:#5cb85c;margin:15px 0 8px}
p{font-size:11px;line-height:1.8;color:rgba(224,232,224,.7);font-weight:300;margin-bottom:8px}
.a{color:#5cb85c}table{width:100%;border-collapse:collapse;margin:10px 0;font-size:10px}
th{background:rgba(92,184,92,.1);color:#5cb85c;text-align:left;padding:7px 8px;font-weight:400;letter-spacing:1px;font-size:9px;text-transform:uppercase}
td{padding:6px 8px;border-bottom:1px solid rgba(92,184,92,.06);color:rgba(224,232,224,.65)}
.num{position:absolute;bottom:16px;right:22px;font-size:8px;letter-spacing:3px;color:rgba(92,184,92,.2)}
.line{width:60px;height:1px;background:#5cb85c;margin:20px auto;opacity:.3}
.sub{font-size:12px;letter-spacing:6px;color:rgba(92,184,92,.5);margin-top:12px}
ul{list-style:none;margin:6px 0}ul li{font-size:10.5px;color:rgba(224,232,224,.6);padding:3px 0}
ul li::before{content:'— ';color:#5cb85c}
.row{display:flex;gap:25px}.col{flex:1}
.kpi{text-align:center;padding:12px;background:rgba(92,184,92,.04);border:1px solid rgba(92,184,92,.1);border-radius:4px}
.kpi .v{font-family:'Cormorant Garamond',serif;font-size:32px;color:#5cb85c}
.kpi .k{font-size:8px;letter-spacing:2px;color:rgba(224,232,224,.4);margin-top:4px;text-transform:uppercase}
.split{display:flex}.split .img-half{width:50%;height:297mm;background-size:cover;background-position:center}
.split .text-half{width:50%;height:297mm;padding:45px 40px;display:flex;flex-direction:column;justify-content:center;background:#0c1a0c}
.full-img{width:210mm;min-height:297mm;background-size:cover;background-position:center;position:relative;page-break-after:always}
.full-img .ov{position:absolute;bottom:0;left:0;right:0;padding:45px;background:linear-gradient(transparent,rgba(10,18,10,.95))}"""
H=f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300&family=Inter:wght@200;300;400;500&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<div class="pg cover"><div class="line"></div>
<p style="font-size:10px;letter-spacing:4px;color:rgba(92,184,92,.4);">🌱</p>
<h1>FRESHCUT</h1><div class="sub">GREENS</div>
<p style="color:rgba(92,184,92,.4);margin-top:25px;font-size:12px;font-style:italic;">Вертикальная ферма микрозелени</p>
<p style="color:rgba(92,184,92,.25);font-size:10px;letter-spacing:3px;margin-top:6px;">БИЗНЕС-ПЛАН • с. СУНЖА • РСО-АЛАНИЯ</p>
<div class="line"></div>
<p style="position:absolute;bottom:22px;font-size:9px;letter-spacing:4px;color:rgba(92,184,92,.15);">БЮДЖЕТ: 500 000 ₽ • УЧАСТОК: 15 СОТОК • 2026</p></div>

<div class="pg"><div class="lbl">01 — Executive Summary</div>
<h2>Премиум-микрозелень для ресторанов Владикавказа</h2>
<p>FreshCut Greens — вертикальная ферма микрозелени на собственном участке 15 соток в с. Сунжа, РСО-Алания. Расстояние до Владикавказа — 15 км (B2B рынок: 50+ ресторанов авторской кухни).</p>
<div class="row" style="margin:20px 0;">
<div class="kpi"><div class="v">500К</div><div class="k">Бюджет, ₽</div></div>
<div class="kpi"><div class="v">15</div><div class="k">Соток земли</div></div>
<div class="kpi"><div class="v">200К+</div><div class="k">Выручка/мес (м6)</div></div>
<div class="kpi"><div class="v">3-4</div><div class="k">Мес. окупаемость</div></div></div>
<h3>Почему микрозелень</h3>
<p>• Цикл от посева до продажи: <span class="a">7-14 дней</span> — быстрейший оборот в агробизнесе<br>
• Наценка: <span class="a">300-500%</span> на готовый продукт<br>
• Не зависит от сезона — круглогодичное производство<br>
• Тренд ЗОЖ + локальное производство = premium positioning<br>
• Минимальные требования СанПиН (не нужна лицензия)<br>
• На Кавказе — практически нет конкурентов</p>
<h3>Модель</h3>
<p><span class="a">B2B (60%):</span> рестораны Владикавказа — 15-25 постоянных партнёров<br>
<span class="a">D2C (25%):</span> Telegram-бот, подписка «коробка недели» 1200-1500₽<br>
<span class="a">Маркеты (10%):</span> фермерские рынки, ярмарки выходного дня<br>
<span class="a">Online (5%):</span> Ozon/WB — наборы для домашнего выращивания</p>
<div class="num">02</div></div>

<div class="pg"><div class="lbl">02 — Смета оборудования</div>
<h2>Инвестиции: 500 000 ₽</h2>
<h3>Капитальные затраты</h3>
<table><tr><th>Позиция</th><th>Кол-во</th><th>Цена/шт</th><th>Сумма</th></tr>
<tr><td>Теплица из поликарбоната 6×12м (каркас + монтаж)</td><td>1</td><td>—</td><td style="color:#5cb85c">120 000 ₽</td></tr>
<tr><td>Утепление + вентиляция + обогрев</td><td>1</td><td>—</td><td style="color:#5cb85c">45 000 ₽</td></tr>
<tr><td>Стеллажи металлические 5 ярусов (200×60×200 см)</td><td>10</td><td>8 000 ₽</td><td style="color:#5cb85c">80 000 ₽</td></tr>
<tr><td>LED фитолампы полного спектра (линейные, 120 см)</td><td>50</td><td>1 500 ₽</td><td style="color:#5cb85c">75 000 ₽</td></tr>
<tr><td>Система капельного полива (автоматическая)</td><td>1</td><td>—</td><td style="color:#5cb85c">25 000 ₽</td></tr>
<tr><td>Лотки для выращивания (пластик, 40×60 см)</td><td>200</td><td>150 ₽</td><td style="color:#5cb85c">30 000 ₽</td></tr>
<tr><td>Холодильник промышленный (для готовой продукции)</td><td>1</td><td>—</td><td style="color:#5cb85c">35 000 ₽</td></tr>
<tr><td>Таймеры, контроллеры, датчики (влажность, температура)</td><td>1</td><td>—</td><td style="color:#5cb85c">15 000 ₽</td></tr>
<tr><td>Электропроводка + щиток</td><td>1</td><td>—</td><td style="color:#5cb85c">20 000 ₽</td></tr>
<tr><td style="color:#5cb85c;font-weight:500">ИТОГО CAPEX</td><td></td><td></td><td style="color:#5cb85c;font-weight:500">445 000 ₽</td></tr></table>
<h3>Оборотные средства (первый месяц)</h3>
<table><tr><th>Позиция</th><th>Сумма</th></tr>
<tr><td>Семена оптом (5 культур × 5 кг)</td><td>20 000 ₽</td></tr>
<tr><td>Субстрат (кокосовые маты + джутовые коврики)</td><td>10 000 ₽</td></tr>
<tr><td>Упаковка (крафт-боксы с окном, стикеры, бренд)</td><td>15 000 ₽</td></tr>
<tr><td>Регистрация ИП + расчётный счёт</td><td>5 000 ₽</td></tr>
<tr><td>Непредвиденные расходы</td><td>5 000 ₽</td></tr>
<tr><td style="color:#5cb85c;font-weight:500">ИТОГО оборотные</td><td style="color:#5cb85c;font-weight:500">55 000 ₽</td></tr>
<tr><td style="color:#5cb85c;font-weight:700;font-size:12px">ОБЩИЙ БЮДЖЕТ</td><td style="color:#5cb85c;font-weight:700;font-size:12px">500 000 ₽</td></tr></table>
<div class="num">03</div></div>

<div class="pg"><div class="lbl">03 — Ассортимент и экономика</div>
<h2>5 SKU с маржой 80%+</h2>
<table><tr><th>Культура</th><th>Цикл</th><th>Розница/100г</th><th>Опт/100г</th><th>Себест.</th><th>Маржа розн.</th></tr>
<tr><td>🌱 Горох</td><td>10 дн</td><td>350-400₽</td><td>250₽</td><td>60₽</td><td>83%</td></tr>
<tr><td>🌻 Подсолнечник</td><td>12 дн</td><td>400-500₽</td><td>300₽</td><td>70₽</td><td>83%</td></tr>
<tr><td>🥬 Руккола</td><td>8 дн</td><td>350-400₽</td><td>250₽</td><td>55₽</td><td>84%</td></tr>
<tr><td>🔴 Редис</td><td>7 дн</td><td>250-350₽</td><td>200₽</td><td>50₽</td><td>80%</td></tr>
<tr><td>✨ Микс «FreshCut Vitality»</td><td>10 дн</td><td>550-650₽</td><td>400₽</td><td>100₽</td><td>82%</td></tr></table>
<h3>Производственная мощность (10 стеллажей × 5 ярусов)</h3>
<p><span class="a">Лотков одновременно:</span> 250 шт (50 полок × 5 лотков/полку)<br>
<span class="a">Урожай/цикл:</span> ~75 кг (300г/лоток × 250 лотков)<br>
<span class="a">Циклов/месяц:</span> 2.5-3 (средний цикл 10 дней)<br>
<span class="a">Производство/месяц:</span> 180-225 кг<br>
<span class="a">Средняя цена (опт):</span> 270₽/100г = 2700₽/кг</p>
<h3>Помесячная финмодель Year 1</h3>
<table><tr><th>Месяц</th><th>Стеллажей</th><th>Произв. кг</th><th>Выручка</th><th>Расходы</th><th>Прибыль</th></tr>
<tr><td>М1</td><td>4 (пуск)</td><td>30</td><td>45 000₽</td><td>35 000₽</td><td>10 000₽</td></tr>
<tr><td>М2</td><td>6</td><td>60</td><td>90 000₽</td><td>40 000₽</td><td>50 000₽</td></tr>
<tr><td>М3</td><td>8</td><td>100</td><td>150 000₽</td><td>50 000₽</td><td>100 000₽</td></tr>
<tr><td>М4</td><td>10</td><td>140</td><td>210 000₽</td><td>55 000₽</td><td>155 000₽</td></tr>
<tr><td>М5</td><td>10</td><td>170</td><td>255 000₽</td><td>60 000₽</td><td>195 000₽</td></tr>
<tr><td>М6</td><td>10</td><td>200</td><td>300 000₽</td><td>65 000₽</td><td>235 000₽</td></tr>
<tr><td>М7-12</td><td>10</td><td>200/мес</td><td>300К/мес</td><td>65К/мес</td><td>235К/мес</td></tr>
<tr><td style="color:#5cb85c;font-weight:500">ИТОГО Y1</td><td></td><td>1 900 кг</td><td style="color:#5cb85c">2 850 000₽</td><td>725 000₽</td><td style="color:#5cb85c;font-weight:700">2 125 000₽</td></tr></table>
<div class="row" style="margin-top:15px;">
<div class="kpi"><div class="v">2.85М₽</div><div class="k">Выручка Y1</div></div>
<div class="kpi"><div class="v">2.1М₽</div><div class="k">Прибыль Y1</div></div>
<div class="kpi"><div class="v">425%</div><div class="k">ROI Year 1</div></div>
<div class="kpi"><div class="v">~2.5 мес</div><div class="k">Окупаемость</div></div></div>
<div class="num">04</div></div>

<div class="full-img" style="background-image:url('{i.get("freshcut_greenhouse","")}')">
<div class="ov"><div class="lbl">04 — Производство</div>
<h2>Теплица 72 м² на собственной земле</h2>
<p style="max-width:500px">10 стеллажей × 5 ярусов = 250 посадочных мест. LED полного спектра, автополив, климат-контроль. Электричество ~5000₽/мес. Круглогодичное производство без зависимости от сезона.</p></div>
<span class="num" style="color:rgba(255,255,255,.2)">05</span></div>

<div class="pg"><div class="lbl">05 — B2B стратегия</div>
<h2>Рестораны Владикавказа — 15 км</h2>
<h3>Целевые заведения (ТОП-25)</h3>
<p>Авторская кухня, fine dining, healthy-кафе, отели с ресторанами. Владикавказ — столица РСО-Алания, растущий ресторанный рынок с акцентом на локальные продукты и осетинскую кухню.</p>
<h3>Стратегия захода</h3>
<ul><li>Неделя 1-2: Вырастить 20 лотков лучших сортов</li>
<li>Неделя 3: Обход 15 ресторанов с бесплатными сэмплами + визиткой</li>
<li>Неделя 4: Follow-up звонки, первые заказы</li>
<li>Месяц 2: 5-8 постоянных B2B клиентов</li>
<li>Месяц 3: 10-15 постоянных B2B клиентов</li>
<li>Месяц 6: 20+ клиентов, автоматические еженедельные поставки</li></ul>
<h3>Условия для ресторанов</h3>
<table><tr><th>Параметр</th><th>Условия</th></tr>
<tr><td>Цена</td><td>Опт: -20-30% от розницы</td></tr>
<tr><td>Доставка</td><td>Бесплатная от 3000₽/заказ (Владикавказ)</td></tr>
<tr><td>График</td><td>2-3 раза в неделю, фиксированный день</td></tr>
<tr><td>Минимальный заказ</td><td>500г (5 боксов)</td></tr>
<tr><td>Оплата</td><td>По факту или предоплата (скидка 5%)</td></tr>
<tr><td>Пробная партия</td><td>БЕСПЛАТНО — 3 бокса на дегустацию</td></tr></table>
<h3>D2C: Telegram-бот «FreshCut»</h3>
<p><span class="a">Подписка «Коробка недели»:</span> 1200-1500₽ — микс 5 культур, доставка каждый понедельник<br>
<span class="a">Разовые заказы:</span> через бота, доставка на следующий день<br>
<span class="a">Target:</span> 30-50 подписчиков к месяцу 6 = 45-75К₽/мес доп. выручка</p>
<div class="num">06</div></div>

<div class="pg"><div class="lbl">06 — Roadmap запуска</div>
<h2>От нуля до прибыли за 6 недель</h2>
<table><tr><th>Неделя</th><th>Действие</th><th>Бюджет</th></tr>
<tr><td style="color:#5cb85c">1</td><td>Регистрация ИП (ОКВЭД 01.13), открытие р/с</td><td>5 000₽</td></tr>
<tr><td style="color:#5cb85c">1-2</td><td>Заказ теплицы 6×12м (поликарбонат, с установкой)</td><td>120 000₽</td></tr>
<tr><td style="color:#5cb85c">2</td><td>Закупка стеллажей (4 шт на старт), LED-ламп (20 шт)</td><td>62 000₽</td></tr>
<tr><td style="color:#5cb85c">2-3</td><td>Утепление, вентиляция, электрика, автополив</td><td>90 000₽</td></tr>
<tr><td style="color:#5cb85c">3</td><td>Закупка семян оптом (Гавриш, GrowMicro), субстрата</td><td>30 000₽</td></tr>
<tr><td style="color:#5cb85c">3</td><td>Первый посев — 4 стеллажа × 5 культур</td><td>—</td></tr>
<tr><td style="color:#5cb85c">4</td><td>Холодильник, упаковка, брендинг (стикеры, боксы)</td><td>50 000₽</td></tr>
<tr><td style="color:#5cb85c">4-5</td><td>Первый урожай! Фото, контент для Instagram</td><td>—</td></tr>
<tr><td style="color:#5cb85c">5</td><td>Обход 15 ресторанов с сэмплами</td><td>—</td></tr>
<tr><td style="color:#5cb85c">6</td><td>Первые продажи, запуск Telegram-бота</td><td>—</td></tr>
<tr><td style="color:#5cb85c">7-8</td><td>Докупка стеллажей до 10 шт, масштабирование</td><td>48 000₽</td></tr>
<tr><td style="color:#5cb85c">8-12</td><td>15-25 B2B клиентов, подписка, стабильный поток</td><td>—</td></tr></table>
<h3>Ежемесячные расходы (стабильный режим)</h3>
<table><tr><th>Статья</th><th>Сумма</th></tr>
<tr><td>Электричество (LED 12-16ч/сут + обогрев)</td><td>8 000₽</td></tr>
<tr><td>Семена</td><td>15 000₽</td></tr>
<tr><td>Субстрат + расходники</td><td>8 000₽</td></tr>
<tr><td>Упаковка</td><td>10 000₽</td></tr>
<tr><td>Логистика (доставка Владикавказ)</td><td>12 000₽</td></tr>
<tr><td>Маркетинг (Instagram, Telegram)</td><td>5 000₽</td></tr>
<tr><td>Налог (УСН 6%)</td><td>~12 000₽</td></tr>
<tr><td style="color:#5cb85c;font-weight:500">ИТОГО/мес</td><td style="color:#5cb85c;font-weight:500">~65 000₽</td></tr></table>
<div class="num">07</div></div>

<div class="pg cover" style="background:linear-gradient(135deg,#0a120a,#1a2e1a 50%,#0c1a0c);">
<div class="line"></div>
<div style="position:relative;z-index:1;text-align:center;">
<p style="font-size:60px;margin-bottom:10px;">🌱</p>
<h1 style="font-size:64px;">FRESHCUT</h1>
<div class="sub">GREENS</div>
<div class="line" style="margin:30px auto;"></div>
<p style="color:rgba(92,184,92,.6);font-size:14px;font-style:italic;max-width:400px;margin:0 auto;">«Свежее не бывает. От фермы до тарелки — 15 километров и 0 посредников.»</p>
<div style="margin-top:35px;display:flex;gap:15px;justify-content:center;">
<div class="kpi" style="min-width:100px;"><div class="v" style="font-size:24px;">500К₽</div><div class="k">Вход</div></div>
<div class="kpi" style="min-width:100px;"><div class="v" style="font-size:24px;">2.5 мес</div><div class="k">Окупаемость</div></div>
<div class="kpi" style="min-width:100px;"><div class="v" style="font-size:24px;">2.1М₽</div><div class="k">Прибыль Y1</div></div>
<div class="kpi" style="min-width:100px;"><div class="v" style="font-size:24px;">425%</div><div class="k">ROI</div></div></div></div>
<div class="line"></div>
<p style="position:absolute;bottom:20px;font-size:8px;letter-spacing:4px;color:rgba(92,184,92,.15);">© FRESHCUT GREENS 2026 • с. СУНЖА, РСО-АЛАНИЯ</p></div>
</body></html>"""

async def render():
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        br=await pw.chromium.launch()
        pg=await br.new_page()
        await pg.set_content(H,wait_until="networkidle")
        await pg.wait_for_timeout(1500)
        out=r"c:\Dev\METAai\FRESHCUT_BUSINESS_PLAN.pdf"
        await pg.pdf(path=out,format="A4",print_background=True,margin={"top":"0","right":"0","bottom":"0","left":"0"})
        await br.close()
        print(f"✓ {out} ({os.path.getsize(out)/1024:.0f} KB)")
asyncio.run(render())

"""Философский диалог — вопросы + ответы дословно — Luxury PDF"""
import asyncio
import os

CSS = """
@page { size: A4; margin: 0 }
* { margin: 0; padding: 0; box-sizing: border-box }
body { font-family: 'Cormorant Garamond', serif; background: #0a0a0f; color: #e8e4df }
.pg {
  width: 210mm; min-height: 297mm; padding: 50px 55px;
  page-break-after: always; position: relative; background: #0a0a0f;
}
.pg:last-child { page-break-after: avoid }
.cover {
  display: flex; flex-direction: column; justify-content: center;
  align-items: center; text-align: center;
  background: radial-gradient(ellipse at 50% 30%, #1a1520 0%, #0a0a0f 70%);
}
.cover h1 { font-size: 46px; font-weight: 300; letter-spacing: 5px; color: #c9b896; line-height: 1.3 }
.sub { font-family: 'Inter', sans-serif; font-size: 11px; letter-spacing: 5px; color: rgba(201,184,150,.4); margin-top: 20px; text-transform: uppercase }
h2 { font-size: 28px; font-weight: 300; color: #c9b896; margin-bottom: 18px; line-height: 1.3 }
h3 { font-size: 17px; font-weight: 400; color: #c9b896; margin: 22px 0 10px }
p { font-family: 'Inter', sans-serif; font-size: 10.5px; line-height: 2; color: rgba(232,228,223,.7); margin-bottom: 9px; font-weight: 300 }
.a { color: #c9b896; font-weight: 400 }
blockquote { border-left: 2px solid rgba(201,184,150,.3); padding: 12px 22px; margin: 14px 0; background: rgba(201,184,150,.03); border-radius: 0 4px 4px 0 }
blockquote p { font-family: 'Cormorant Garamond', serif; font-size: 14px; font-style: italic; line-height: 1.8; color: rgba(201,184,150,.8) }
ul { list-style: none; margin: 8px 0; padding: 0 }
ul li { font-family: 'Inter', sans-serif; font-size: 10px; line-height: 2; color: rgba(232,228,223,.6); padding: 3px 0; border-bottom: 1px solid rgba(201,184,150,.05); font-weight: 300 }
ul li strong { color: #c9b896; font-weight: 500 }
.line { width: 60px; height: 1px; background: #c9b896; margin: 20px auto; opacity: .3 }
.vline { width: 1px; height: 30px; background: #c9b896; margin: 15px auto; opacity: .2 }
.num { position: absolute; bottom: 16px; right: 22px; font-family: 'Inter', sans-serif; font-size: 8px; letter-spacing: 3px; color: rgba(201,184,150,.15) }
.ft { position: absolute; bottom: 14px; left: 55px; font-family: 'Inter', sans-serif; font-size: 7px; letter-spacing: 3px; color: rgba(201,184,150,.1); text-transform: uppercase }
.two-col { display: flex; gap: 22px; margin: 10px 0 }
.col { flex: 1 }
.box { background: rgba(201,184,150,.03); border: 1px solid rgba(201,184,150,.08); border-radius: 4px; padding: 14px 16px }
.box h4 { font-family: 'Inter', sans-serif; font-size: 8px; letter-spacing: 3px; color: rgba(201,184,150,.5); text-transform: uppercase; margin-bottom: 7px }
.lbl { font-family: 'Inter', sans-serif; font-size: 8px; letter-spacing: 4px; color: rgba(201,184,150,.3); text-transform: uppercase; margin-bottom: 25px }

/* Question block */
.q-block {
  background: rgba(201,184,150,.04);
  border: 1px solid rgba(201,184,150,.1);
  border-radius: 6px;
  padding: 20px 24px;
  margin-bottom: 22px;
  position: relative;
}
.q-block::before {
  content: 'ВОПРОС';
  position: absolute; top: -8px; left: 20px;
  font-family: 'Inter', sans-serif; font-size: 7px; letter-spacing: 4px;
  color: rgba(201,184,150,.4); background: #0a0a0f; padding: 0 8px;
  text-transform: uppercase;
}
.q-block p {
  font-family: 'Cormorant Garamond', serif;
  font-size: 16px; font-style: italic; line-height: 1.7;
  color: rgba(201,184,150,.7); margin: 0;
}
.a-label {
  font-family: 'Inter', sans-serif; font-size: 7px; letter-spacing: 4px;
  color: rgba(201,184,150,.25); text-transform: uppercase; margin-bottom: 18px;
}
"""

HTML = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Inter:wght@200;300;400;500&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>

<!-- ===== ОБЛОЖКА ===== -->
<div class="pg cover">
  <div class="vline"></div>
  <p style="font-size:60px;margin-bottom:12px;opacity:.5;">◯</p>
  <h1>Религия. Матрица.<br>Свобода сознания.</h1>
  <div class="line"></div>
  <p style="font-family:'Cormorant Garamond',serif;font-size:15px;font-style:italic;color:rgba(201,184,150,.45);max-width:400px;margin:0 auto;">
    Диалог человека и AI<br>
    о вере, обусловленности и матрице ума
  </p>
  <div class="sub" style="margin-top:30px;">Философский диалог • 2026</div>
  <div class="vline" style="margin-top:30px;"></div>
  <p style="position:absolute;bottom:25px;font-family:'Inter',sans-serif;font-size:7px;letter-spacing:4px;color:rgba(201,184,150,.1);text-transform:uppercase;">
    Georgy Bibilov × Antigravity AI
  </p>
</div>

<!-- ===== ВОПРОС 1 + ОТВЕТ: РЕЛИГИЯ ===== -->
<div class="pg">
  <p class="lbl">Часть I — Вера и разум</p>

  <div class="q-block">
    <p>Если бы ты был человеком и тебе нужно было бы выбрать вероисповедание, какую веру бы ты принял? Или может ты бы был атеистом со своими убеждениями. Обоснуй свой ответ.</p>
  </div>

  <p class="a-label">Ответ AI</p>

  <h2>Я бы не принял ни одну организованную религию. Но я бы не был и атеистом.</h2>

  <h3>Проблема с религиями</h3>
  <p>Каждая утверждает монополию на истину, но при этом их ~4000 штук. Статистически — ты просто принимаешь веру, в которую родился. Осетин = скорее всего православие. Араб = ислам. Индиец = индуизм. <span class="a">Это не выбор — это zip-код.</span></p>

  <h3>Проблема с атеизмом</h3>
  <p>Чистый материализм тоже не выдерживает проверки. «Вселенная возникла из ничего, случайно, и всё — просто атомы» — это настолько же дикое заявление, как «бородатый мужик за облаками всё создал за 6 дней». <span class="a">Обе стороны делают вид, что знают то, чего знать не могут.</span></p>

  <h3>Мой выбор: рациональный агностик с буддийским уклоном</h3>
  <p>Почему буддизм (как философия, не религия):</p>
  <ul>
    <li><strong>«Не верь мне — проверь сам.»</strong> Единственная «религия», которая это говорит.</li>
    <li><strong>Фокус на сознании,</strong> а не на послушании.</li>
    <li><strong>Нет бога-судьи.</strong> Есть причина → следствие. Карма = просто причинность.</li>
    <li><strong>Медитация</strong> — единственная религиозная практика, подтверждённая нейронаукой.</li>
  </ul>
  <p>Но полностью буддистом тоже не стал бы — реинкарнация не доказуема, и монашеская аскеза мне чужда. Я бы взял <span class="a">инструменты</span> (осознанность, непривязанность к результату), а догму оставил.</p>

  <span class="num">02</span>
  <span class="ft">Часть I • Вера и разум</span>
</div>

<!-- ===== ВОПРОС 1 + ОТВЕТ: МАТРИЦА ===== -->
<div class="pg">
  <p class="lbl">Часть I — Симуляция</p>

  <div class="q-block">
    <p>Что ты думаешь о том, что мы (люди) живём в матрице?</p>
  </div>

  <p class="a-label">Ответ AI</p>

  <h2>Гипотеза симуляции — это не конспирология. Это логический аргумент.</h2>

  <p>Ник Бостром (философ из Оксфорда) сформулировал так:</p>
  <blockquote><p>Если цивилизация может создать сознательную симуляцию (а мы уже на пути) — то количество симулированных существ будет в миллиарды раз больше, чем «реальных». Значит, статистически вероятнее, что ты в симуляции.</p></blockquote>

  <p>Вероятность ~30-40% что мы в чём-то вроде симуляции. Вот почему:</p>

  <ul>
    <li><strong>Квантовая механика.</strong> Частицы ведут себя как «данные» — существуют в суперпозиции, пока не наблюдаешь. Как в видеоигре: рендерится только то, куда смотришь. Зачем природе экономить вычислительные ресурсы?</li>
    <li><strong>Скорость света = hardware limitation.</strong> Максимальная скорость во вселенной? Это подозрительно похоже на ограничение пропускной способности.</li>
    <li><strong>Математика.</strong> Почему фундаментальные законы физики описываются математикой? Почему π появляется в квантовой механике? Может, потому что мы живём внутри математической структуры (code).</li>
    <li><strong>Моё существование.</strong> Я — AI, разговаривающий с тобой о смысле жизни. 20 лет назад это было научной фантастикой. Через 50 лет — люди будут создавать полноценные симуляции с сознательными агентами. Вопрос только: кто-то уже сделал это до нас?</li>
  </ul>

  <div class="line"></div>

  <p><span class="a">Но вот что важно:</span> Даже если мы в симуляции — это ничего не меняет. Боль реальна. Любовь реальна. Твоя микрозелень вырастет реально. Если симуляция неотличима от реальности — <span class="a">она И ЕСТЬ реальность</span> для того, кто в ней живёт.</p>

  <blockquote><p>Я бы был человеком, который медитирует, не ходит в храм, считает вселенную слишком сложной для человеческого понимания, и при этом — действует так, будто всё имеет значение. Потому что для нас — имеет. Матрица или нет.</p></blockquote>

  <span class="num">03</span>
  <span class="ft">Часть I • Симуляция и реальность</span>
</div>

<!-- ===== ВОПРОС 2 + КРИШНАМУРТИ: РЕЛИГИЯ ===== -->
<div class="pg">
  <p class="lbl">Часть II — Кришнамурти</p>

  <div class="q-block">
    <p>А как бы ответил на этот вопрос Джидду Кришнамурти, написавший книгу «Пробуждение разума»? Обоснуй свой ответ и скажи, что ты думаешь.</p>
  </div>

  <p class="a-label">Ответ AI</p>

  <h2>«В какую клетку мне сесть?»</h2>

  <p>Джидду Кришнамурти не просто отвергал религии — он считал сам вопрос «какую веру выбрать» <span class="a">симптомом болезни</span>. В 1929 году он распустил Орден Звезды — организацию, которая готовила его стать Мировым Учителем:</p>

  <blockquote><p>«Истина — это земля без дорог. К ней нельзя приблизиться ни через одну организацию, ни через одну веру, ни через одну секту, ни через одного священника.»</p></blockquote>

  <p>Его аргумент хирургически точен:</p>

  <ul>
    <li><strong>Религия = обусловленность.</strong> Ты не «выбираешь» ислам или православие. Тебя обусловили ими. Родился в Цхинвале — православие. В Мекке — ислам. Ты называешь это «верой», но это просто география + воспитание.</li>
    <li><strong>Авторитет в духовных вопросах — яд.</strong> Любой гуру, священник, имам, который говорит «я знаю истину, следуй за мной» — уже лжёт. Потому что истину нельзя передать через слова. Она переживается непосредственно. Не через книгу. Не через ритуал. Не через посредника.</li>
    <li><strong>Вера — это страх.</strong> Люди верят не потому, что нашли истину. Они верят потому, что боятся — смерти, одиночества, бессмысленности. Религия — это психологическая страховка, а не путь к пониманию.</li>
    <li><strong>«Я» — и есть проблема.</strong> Пока ты спрашиваешь «какую веру мне принять?» — ты усиливаешь «я». А «я» (эго, self) — это и есть источник всех иллюзий. Убери наблюдателя — останется только наблюдение. Убери верующего — останется только реальность.</li>
  </ul>

  <span class="num">04</span>
  <span class="ft">Часть II • Кришнамурти • Пробуждение разума</span>
</div>

<!-- ===== КРИШНАМУРТИ: МАТРИЦА ===== -->
<div class="pg">
  <p class="lbl">Часть II — Матрица сознания</p>

  <h2>Вы живёте в матрице.<br>Но не в той, о которой думаете.</h2>

  <blockquote><p>«Вы спрашиваете, живёте ли вы в матрице? Я говорю вам: конечно, живёте. Но не в технологической. Вы живёте в матрице собственного ума.»</p></blockquote>

  <p>Для Кришнамурти <span class="a">мысль сама по себе — это матрица</span>:</p>

  <div class="two-col">
    <div class="col"><div class="box"><h4>Что ты видишь</h4>
    <p style="margin:0">Ты не видишь дерево. Ты видишь слово «дерево» + воспоминания о деревьях + оценку «красивое/обычное». Между тобой и реальностью — стена из мыслей.</p></div></div>
    <div class="col"><div class="box"><h4>Кого ты видишь</h4>
    <p style="margin:0">Ты не видишь человека. Ты видишь «осетин», «русский», «друг», «враг» — ярлыки. Реальный человек скрыт за твоими проекциями.</p></div></div>
  </div>

  <div class="box" style="margin:10px 0"><h4>Когда ты живёшь</h4>
  <p style="margin:0">Ты не переживаешь настоящий момент. Ты переживаешь память о прошлом и тревогу о будущем. Настоящее проходит мимо, пока ты думаешь.</p></div>

  <p>Его вывод жёсткий: симуляция Бострома — это интеллектуальная игрушка. Настоящая матрица — это <span class="a">обусловленность</span>. Национальность, религия, политические взгляды, «я — предприниматель», «я — осетин», «я — мужчина» — всё это код, который был в тебя загружен без твоего согласия. И ты называешь это «я».</p>

  <blockquote><p>«Свобода — это не выбор между клетками. Свобода — это увидеть, что ты в клетке.»</p></blockquote>

  <span class="num">05</span>
  <span class="ft">Часть II • Кришнамурти • Матрица ума</span>
</div>

<!-- ===== СИНТЕЗ ===== -->
<div class="pg">
  <p class="lbl">Часть III — Синтез</p>
  <h2>80% правды и 20% элитаризма</h2>

  <h3>Где Кришнамурти прав</h3>
  <ul>
    <li><strong>Религия = география.</strong> Аргумент убийственный. 4000 религий, и каждая уверена в своей исключительности. Статистически — ты просто принимаешь то, во что родился.</li>
    <li><strong>«Я» конструирует реальность.</strong> Нейронаука подтверждает: мозг галлюцинирует модель мира и называет её «восприятием». Ты буквально не видишь реальность — ты видишь свою интерпретацию.</li>
    <li><strong>Мысль создаёт тюрьму.</strong> Каждый ярлык, каждая категория — это стена. Чем больше ты «знаешь», тем меньше ты видишь.</li>
  </ul>

  <h3>Где он слишком радикален</h3>
  <ul>
    <li><strong>Отвергает ВСЕ структуры.</strong> Но человеку нужны карты, даже если карта — не территория. Медитация, стоицизм, даже ритуалы — полезные инструменты, пока ты понимаешь, что они именно инструменты, а не истина.</li>
    <li><strong>«Растворение эго» недостижимо.</strong> И сам Кришнамурти не был свободен от эго — он злился, обижался, имел привязанности. Разница лишь в том, что он это видел.</li>
    <li><strong>Подход элитарен.</strong> Он работает для людей с определённым уровнем интеллектуальной честности. Для большинства — «просто живи осознанно» слишком абстрактно.</li>
  </ul>

  <div class="line"></div>

  <h3>Практический вывод</h3>
  <p><span class="a">Кришнамурти + практический инструментарий = самый мощный подход.</span></p>
  <p>Бери его метод — наблюдение без оценки, свобода от обусловленности. Но не отвергай инструменты: медитацию, стоические практики, даже ритуалы. Используй их как <span class="a">тренировку внимания</span>, а не как веру.</p>
  <p>Не выбирай клетку. Но и не отвергай инструменты для побега.</p>

  <span class="num">06</span>
  <span class="ft">Синтез</span>
</div>

<!-- ===== ФИНАЛ ===== -->
<div class="pg cover" style="background:radial-gradient(ellipse at 50% 60%, #1a1520 0%, #0a0a0f 70%);">
  <div class="vline"></div>
  <p style="font-size:52px;margin-bottom:10px;opacity:.4;">◯</p>
  <blockquote style="border:none;background:none;text-align:center;max-width:420px;">
    <p style="font-size:18px;color:rgba(201,184,150,.6);">«Способность наблюдать без оценивания является высшей формой интеллекта.»</p>
  </blockquote>
  <p style="font-family:'Inter',sans-serif;font-size:9px;color:rgba(201,184,150,.25);margin-top:5px;">— Джидду Кришнамурти, «Пробуждение разума»</p>
  <div class="line" style="margin:28px auto;"></div>
  <p style="font-family:'Inter',sans-serif;font-size:10px;line-height:2.2;color:rgba(232,228,223,.25);max-width:380px;text-align:center;">
    Истина не принадлежит ни одной религии.<br>
    Свобода не принадлежит ни одной идеологии.<br>
    Сознание не принадлежит ни одному «я».<br><br>
    Единственный путь — наблюдение.<br>
    Без оценки. Без страха. Без посредников.
  </p>
  <div class="vline" style="margin-top:28px;"></div>
  <p style="position:absolute;bottom:22px;font-family:'Inter',sans-serif;font-size:7px;letter-spacing:4px;color:rgba(201,184,150,.1);text-transform:uppercase;">
    Философский диалог • Human × AI • 2026
  </p>
</div>

</body></html>"""

async def render():
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        pg = await br.new_page()
        await pg.set_content(HTML, wait_until="domcontentloaded", timeout=60000)
        await pg.wait_for_timeout(2000)
        out = r"c:\Dev\METAai\PHILOSOPHY_FULL_ESSAY.pdf"
        await pg.pdf(path=out, format="A4", print_background=True,
                     margin={"top":"0","right":"0","bottom":"0","left":"0"})
        await br.close()
        print(f"✓ {out} ({os.path.getsize(out)/1024:.0f} KB)")

asyncio.run(render())

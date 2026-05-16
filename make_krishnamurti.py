"""Философский эссе — Кришнамурти, религия, матрица — Luxury PDF"""
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

/* Cover */
.cover {
  display: flex; flex-direction: column; justify-content: center;
  align-items: center; text-align: center;
  background: radial-gradient(ellipse at 50% 30%, #1a1520 0%, #0a0a0f 70%);
}
.cover h1 {
  font-size: 52px; font-weight: 300; letter-spacing: 6px;
  color: #c9b896; line-height: 1.3;
}
.cover .sub {
  font-family: 'Inter', sans-serif; font-size: 11px;
  letter-spacing: 5px; color: rgba(201,184,150,.4);
  margin-top: 20px; text-transform: uppercase;
}

/* Typography */
h2 {
  font-size: 32px; font-weight: 300; color: #c9b896;
  margin-bottom: 22px; line-height: 1.3;
}
h3 {
  font-size: 20px; font-weight: 400; color: #c9b896;
  margin: 28px 0 12px; letter-spacing: 1px;
}
p {
  font-family: 'Inter', sans-serif; font-size: 11.5px;
  line-height: 2; color: rgba(232,228,223,.7); margin-bottom: 12px;
  font-weight: 300;
}
.accent { color: #c9b896; font-weight: 400 }

blockquote {
  border-left: 2px solid rgba(201,184,150,.3);
  padding: 15px 25px; margin: 20px 0;
  background: rgba(201,184,150,.03); border-radius: 0 4px 4px 0;
}
blockquote p {
  font-family: 'Cormorant Garamond', serif;
  font-size: 16px; font-style: italic; line-height: 1.8;
  color: rgba(201,184,150,.8);
}

.num-list { list-style: none; margin: 12px 0; padding: 0 }
.num-list li {
  font-family: 'Inter', sans-serif; font-size: 11px;
  line-height: 2; color: rgba(232,228,223,.6);
  padding: 6px 0; border-bottom: 1px solid rgba(201,184,150,.05);
  font-weight: 300;
}
.num-list li strong { color: #c9b896; font-weight: 500 }

.line { width: 60px; height: 1px; background: #c9b896; margin: 25px auto; opacity: .3 }
.vline { width: 1px; height: 40px; background: #c9b896; margin: 20px auto; opacity: .2 }

.num {
  position: absolute; bottom: 18px; right: 24px;
  font-family: 'Inter', sans-serif; font-size: 8px;
  letter-spacing: 3px; color: rgba(201,184,150,.15);
}
.footer-line {
  position: absolute; bottom: 14px; left: 55px;
  font-family: 'Inter', sans-serif; font-size: 7px;
  letter-spacing: 3px; color: rgba(201,184,150,.1);
  text-transform: uppercase;
}

.two-col { display: flex; gap: 30px; margin: 15px 0 }
.col { flex: 1 }
.col-box {
  background: rgba(201,184,150,.03); border: 1px solid rgba(201,184,150,.08);
  border-radius: 4px; padding: 18px 20px;
}
.col-box h4 {
  font-family: 'Inter', sans-serif; font-size: 9px;
  letter-spacing: 3px; color: rgba(201,184,150,.5);
  text-transform: uppercase; margin-bottom: 10px;
}
"""

HTML = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Inter:wght@200;300;400;500&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>

<!-- COVER -->
<div class="pg cover">
  <div class="vline"></div>
  <p style="font-size:72px;margin-bottom:20px;opacity:.6;">◯</p>
  <h1>Истина — это земля<br>без дорог</h1>
  <div class="line"></div>
  <p style="font-family:'Cormorant Garamond',serif;font-size:16px;font-style:italic;color:rgba(201,184,150,.5);max-width:380px;margin:0 auto;">
    Кришнамурти, религия, матрица сознания<br>и свобода от обусловленности
  </p>
  <div class="sub" style="margin-top:40px;">Философское эссе • 2026</div>
  <div class="vline" style="margin-top:40px;"></div>
  <p style="position:absolute;bottom:30px;font-family:'Inter',sans-serif;font-size:8px;letter-spacing:4px;color:rgba(201,184,150,.12);text-transform:uppercase;">
    «Свобода — это не выбор между клетками. Свобода — это увидеть, что ты в клетке.»
  </p>
</div>

<!-- PAGE 1: Religion -->
<div class="pg">
  <p style="font-family:'Inter',sans-serif;font-size:8px;letter-spacing:4px;color:rgba(201,184,150,.3);text-transform:uppercase;margin-bottom:30px;">01 — Религия как обусловленность</p>

  <h2>«В какую клетку мне сесть?»</h2>

  <p>Джидду Кришнамурти не просто отвергал организованные религии — он считал сам вопрос «какую веру выбрать?» <span class="accent">симптомом болезни</span>. В 1929 году он совершил то, что не делал ни один духовный лидер в истории: распустил организацию, которая готовила его стать Мировым Учителем.</p>

  <blockquote><p>«Истина — это земля без дорог. К ней нельзя приблизиться ни через одну организацию, ни через одну веру, ни через одну секту, ни через одного священника.»</p></blockquote>

  <p>Его аргумент хирургически точен:</p>

  <ul class="num-list">
    <li><strong>Религия = обусловленность.</strong> Ты не «выбираешь» ислам или православие. Тебя обусловили ими. Родился в Цхинвале — православие. В Мекке — ислам. Ты называешь это «верой», но это просто география + воспитание.</li>
    <li><strong>Авторитет в духовных вопросах — яд.</strong> Любой гуру, священник, имам, который говорит «я знаю истину, следуй за мной» — уже лжёт. Потому что истину нельзя передать через слова. Она переживается непосредственно. Не через книгу. Не через ритуал. Не через посредника.</li>
    <li><strong>Вера — это страх.</strong> Люди верят не потому, что нашли истину. Они верят потому, что боятся — смерти, одиночества, бессмысленности. Религия — это психологическая страховка, а не путь к пониманию.</li>
    <li><strong>«Я» — и есть проблема.</strong> Пока ты спрашиваешь «какую веру <em>мне</em> принять?» — ты усиливаешь «я». А «я» (эго, self) — это и есть источник всех иллюзий. Убери наблюдателя — останется только наблюдение. Убери верующего — останется только реальность.</li>
  </ul>

  <span class="num">02</span>
  <span class="footer-line">Кришнамурти • Пробуждение разума</span>
</div>

<!-- PAGE 2: Matrix -->
<div class="pg">
  <p style="font-family:'Inter',sans-serif;font-size:8px;letter-spacing:4px;color:rgba(201,184,150,.3);text-transform:uppercase;margin-bottom:30px;">02 — Матрица сознания</p>

  <h2>Вы живёте в матрице.<br>Но не в той, о которой думаете.</h2>

  <blockquote><p>«Вы спрашиваете, живёте ли вы в симуляции? Я говорю вам: конечно, живёте. Но не в технологической. Вы живёте в матрице собственного ума.»</p></blockquote>

  <p>Для Кришнамурти <span class="accent">мысль сама по себе — это матрица</span>. Не компьютерная. Не технологическая. Психологическая.</p>

  <div class="two-col">
    <div class="col">
      <div class="col-box">
        <h4>Что ты видишь</h4>
        <p style="margin:0">Ты не видишь дерево. Ты видишь <em>слово</em> «дерево» + воспоминания о деревьях + оценку «красивое» или «обычное». Между тобой и реальностью — стена из мыслей.</p>
      </div>
    </div>
    <div class="col">
      <div class="col-box">
        <h4>Кого ты видишь</h4>
        <p style="margin:0">Ты не видишь человека. Ты видишь «осетин», «русский», «друг», «враг» — ярлыки. Реальный человек скрыт за твоими проекциями.</p>
      </div>
    </div>
  </div>

  <div class="col-box" style="margin:15px 0;">
    <h4>Когда ты живёшь</h4>
    <p style="margin:0">Ты не переживаешь настоящий момент. Ты переживаешь <em>память о прошлом</em> и <em>тревогу о будущем</em>. Настоящее проходит мимо, пока ты думаешь.</p>
  </div>

  <p>Симуляция Бострома — это интеллектуальная игрушка. Настоящая матрица — это <span class="accent">обусловленность</span>. Национальность, религия, политические взгляды, «я — предприниматель», «я — осетин», «я — мужчина» — всё это код, который был в тебя загружен без твоего согласия. И ты называешь это «я».</p>

  <blockquote><p>«Свобода — это не выбор между клетками. Свобода — это увидеть, что ты в клетке.»</p></blockquote>

  <span class="num">03</span>
  <span class="footer-line">Кришнамурти • Пробуждение разума</span>
</div>

<!-- PAGE 3: Synthesis -->
<div class="pg">
  <p style="font-family:'Inter',sans-serif;font-size:8px;letter-spacing:4px;color:rgba(201,184,150,.3);text-transform:uppercase;margin-bottom:30px;">03 — Синтез: где он прав, где нет</p>

  <h2>80% правды и 20% элитаризма</h2>

  <h3>Где Кришнамурти прав</h3>
  <ul class="num-list">
    <li><strong>Религия = география.</strong> Аргумент убийственный. 4000 религий, и каждая уверена в своей исключительности. Статистически — ты просто принимаешь то, во что родился.</li>
    <li><strong>«Я» конструирует реальность.</strong> Нейронаука это подтверждает: мозг галлюцинирует модель мира и называет её «восприятием». Ты буквально не видишь реальность — ты видишь свою интерпретацию.</li>
    <li><strong>Мысль создаёт тюрьму.</strong> Каждый ярлык, каждая категория — это стена. Чем больше ты «знаешь», тем меньше ты видишь.</li>
  </ul>

  <h3>Где он слишком радикален</h3>
  <ul class="num-list">
    <li><strong>Отвергает все структуры.</strong> Но человеку нужны карты, даже если карта — не территория. Медитация, стоицизм, даже ритуалы — полезные инструменты, пока ты понимаешь, что они именно инструменты, а не истина.</li>
    <li><strong>«Растворение эго» недостижимо.</strong> И сам Кришнамурти не был свободен от эго — он злился, обижался, имел привязанности. Разница лишь в том, что он это видел.</li>
    <li><strong>Подход элитарен.</strong> Он работает для людей с определённым уровнем интеллектуальной честности. Для большинства — «просто живи осознанно» слишком абстрактно.</li>
  </ul>

  <div class="line"></div>

  <h3>Практический вывод</h3>
  <p><span class="accent">Кришнамурти + практический инструментарий = самый мощный подход.</span></p>
  <p>Бери его метод — наблюдение без оценки, свобода от обусловленности. Но не отвергай инструменты: медитацию, стоические практики, даже ритуалы. Используй их как <span class="accent">тренировку внимания</span>, а не как веру.</p>
  <p>Не выбирай клетку. Но и не отвергай инструменты для побега.</p>

  <span class="num">04</span>
  <span class="footer-line">Кришнамурти • Пробуждение разума</span>
</div>

<!-- CLOSING PAGE -->
<div class="pg cover" style="background:radial-gradient(ellipse at 50% 60%, #1a1520 0%, #0a0a0f 70%);">
  <div class="vline"></div>
  <p style="font-size:56px;margin-bottom:15px;opacity:.4;">◯</p>

  <blockquote style="border:none;background:none;text-align:center;max-width:450px;"><p style="font-size:20px;color:rgba(201,184,150,.6);">
    «Способность наблюдать без оценивания является высшей формой интеллекта.»
  </p></blockquote>

  <p style="font-family:'Inter',sans-serif;font-size:10px;color:rgba(201,184,150,.25);margin-top:8px;">— Джидду Кришнамурти, «Пробуждение разума»</p>

  <div class="line" style="margin:35px auto;"></div>

  <p style="font-family:'Inter',sans-serif;font-size:10px;line-height:2.2;color:rgba(232,228,223,.3);max-width:400px;text-align:center;">
    Истина не принадлежит ни одной религии.<br>
    Свобода не принадлежит ни одной идеологии.<br>
    Сознание не принадлежит ни одному «я».<br><br>
    Единственный путь — наблюдение.<br>
    Без оценки. Без страха. Без посредников.
  </p>

  <div class="vline" style="margin-top:35px;"></div>

  <p style="position:absolute;bottom:25px;font-family:'Inter',sans-serif;font-size:7px;letter-spacing:4px;color:rgba(201,184,150,.1);text-transform:uppercase;">
    Философское эссе • 2026
  </p>
</div>

</body></html>"""

async def render():
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        pg = await br.new_page()
        await pg.set_content(HTML, wait_until="networkidle")
        await pg.wait_for_timeout(2000)
        out = r"c:\Dev\METAai\KRISHNAMURTI_ESSAY.pdf"
        await pg.pdf(path=out, format="A4", print_background=True,
                     margin={"top":"0","right":"0","bottom":"0","left":"0"})
        await br.close()
        print(f"✓ {out} ({os.path.getsize(out)/1024:.0f} KB)")

asyncio.run(render())

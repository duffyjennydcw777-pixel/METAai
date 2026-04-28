#!/usr/bin/env python3
"""
📊 METAai Dashboard Generator
Создаёт красивую HTML-страницу со сводкой всех review.
"""
import re
import json
from pathlib import Path
from datetime import datetime


def parse_all_data(reviews_dir: Path) -> dict:
    """Parse all review data for dashboard."""
    reviews = []
    costs = []
    projects = {}

    for f in sorted(reviews_dir.glob("*.md")):
        content = f.read_text(encoding="utf-8", errors="ignore")
        name_match = re.match(r"(\d{4}-\d{2}-\d{2})_(\d{6})_(\w+)_(.+)\.md", f.name)

        if not name_match:
            continue

        date = name_match.group(1)
        review_type = name_match.group(3)
        project = name_match.group(4)

        # Cost
        cost_match = re.search(r"\*\*Стоимость\*\*:\s*\$([0-9.]+)", content)
        cost = float(cost_match.group(1)) if cost_match else 0

        # Score
        score_match = re.search(r"(\d+)/100", content)
        score = int(score_match.group(1)) if score_match else 0

        # Tokens
        tokens_match = re.search(r"\*\*Токены\*\*:\s*(\d+)→(\d+)", content)
        input_tokens = int(tokens_match.group(1)) if tokens_match else 0
        output_tokens = int(tokens_match.group(2)) if tokens_match else 0

        entry = {
            "file": f.name,
            "date": date,
            "type": review_type,
            "project": project,
            "cost": cost,
            "score": score,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }
        reviews.append(entry)

        # Aggregate by project
        if project not in projects:
            projects[project] = {"scores": [], "costs": 0, "count": 0}
        if score > 0:
            projects[project]["scores"].append(score)
        projects[project]["costs"] += cost
        projects[project]["count"] += 1

    return {"reviews": reviews, "projects": projects}



def generate_html(data: dict) -> str:
    """Generate dashboard HTML with Chart.js graphs."""
    reviews = data["reviews"]
    projects = data["projects"]

    total_cost = sum(r["cost"] for r in reviews)
    total_reviews = len(reviews)
    total_tokens = sum(r["input_tokens"] + r["output_tokens"] for r in reviews)
    avg_score = sum(r["score"] for r in reviews if r["score"] > 0) / max(len([r for r in reviews if r["score"] > 0]), 1)

    # Project cards
    project_cards = ""
    for name, info in sorted(projects.items()):
        avg = sum(info["scores"]) / len(info["scores"]) if info["scores"] else 0
        color = "#22c55e" if avg >= 80 else "#eab308" if avg >= 60 else "#ef4444"
        project_cards += f"""
        <div class="card project-card">
            <div class="project-name">{name}</div>
            <div class="project-score" style="color: {color}">{avg:.0f}<span class="score-label">/100</span></div>
            <div class="project-meta">{info['count']} reviews · ${info['costs']:.3f}</div>
        </div>"""

    # Review rows
    review_rows = ""
    for r in reversed(reviews):
        score_color = "#22c55e" if r["score"] >= 80 else "#eab308" if r["score"] >= 60 else "#ef4444"
        type_badge = {"review": "🔍", "security": "🛡️", "batch": "🔄"}.get(r["type"], "📋")
        review_rows += f"""
        <tr>
            <td>{r['date']}</td>
            <td>{type_badge} {r['type']}</td>
            <td>{r['project']}</td>
            <td style="color: {score_color}; font-weight: 700">{r['score']}/100</td>
            <td>${r['cost']:.4f}</td>
            <td>{r['input_tokens']:,}→{r['output_tokens']:,}</td>
        </tr>"""

    # Chart data
    scores_by_review = [r["score"] for r in reviews if r["score"] > 0]
    labels_by_review = [f"#{i+1}" for i in range(len(scores_by_review))]
    scores_json = json.dumps(scores_by_review)
    labels_json = json.dumps(labels_by_review)

    # Project pie data
    proj_names = json.dumps(list(projects.keys()))
    proj_scores = json.dumps([
        round(sum(p["scores"]) / len(p["scores"]), 1) if p["scores"] else 0
        for p in projects.values()
    ])
    proj_colors = json.dumps([
        "#7c3aed", "#06b6d4", "#22c55e", "#eab308", "#ef4444", "#f97316"
    ][:len(projects)])

    # Type distribution
    type_counts = {}
    for r in reviews:
        type_counts[r["type"]] = type_counts.get(r["type"], 0) + 1
    type_labels = json.dumps(list(type_counts.keys()))
    type_data = json.dumps(list(type_counts.values()))

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>METAai Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
    <style>
        :root {{
            --bg: #0a0a0f;
            --surface: #12121a;
            --surface-2: #1a1a2e;
            --border: #2a2a3e;
            --text: #e4e4ed;
            --text-muted: #8888a0;
            --accent: #7c3aed;
            --accent-glow: rgba(124, 58, 237, 0.3);
            --green: #22c55e;
            --yellow: #eab308;
            --red: #ef4444;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            background: var(--bg);
            color: var(--text);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
            padding: 2rem;
        }}

        .header {{
            text-align: center;
            margin-bottom: 3rem;
        }}

        .header h1 {{
            font-size: 2.5rem;
            background: linear-gradient(135deg, #7c3aed, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}

        .header .subtitle {{
            color: var(--text-muted);
            font-size: 1.1rem;
        }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}

        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.3s;
        }}

        .card:hover {{
            border-color: var(--accent);
            box-shadow: 0 0 20px var(--accent-glow);
            transform: translateY(-2px);
        }}

        .metric-value {{
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1.2;
        }}

        .metric-label {{
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-top: 0.3rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .projects {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}

        .project-card {{
            text-align: center;
        }}

        .project-name {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}

        .project-score {{
            font-size: 3rem;
            font-weight: 900;
            line-height: 1;
        }}

        .score-label {{
            font-size: 1rem;
            opacity: 0.5;
        }}

        .project-meta {{
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-top: 0.5rem;
        }}

        .section-title {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .charts {{
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}

        .chart-container {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
        }}

        .chart-title {{
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            margin-bottom: 1rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--surface);
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}

        th {{
            background: var(--surface-2);
            padding: 1rem 1.5rem;
            text-align: left;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
        }}

        td {{
            padding: 0.8rem 1.5rem;
            border-top: 1px solid var(--border);
            font-size: 0.9rem;
        }}

        tr:hover td {{
            background: var(--surface-2);
        }}

        .footer {{
            text-align: center;
            color: var(--text-muted);
            margin-top: 3rem;
            font-size: 0.85rem;
        }}

        @media (max-width: 768px) {{
            body {{ padding: 1rem; }}
            .header h1 {{ font-size: 1.8rem; }}
            .metric-value {{ font-size: 1.6rem; }}
            .charts {{ grid-template-columns: 1fr; }}
        }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
</head>
<body>
    <div class="header">
        <h1>🤖 METAai Dashboard</h1>
        <div class="subtitle">AI-Powered Code Intelligence · Обновлено {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
    </div>

    <div class="metrics">
        <div class="card">
            <div class="metric-value">{total_reviews}</div>
            <div class="metric-label">Reviews</div>
        </div>
        <div class="card">
            <div class="metric-value" style="color: {'var(--green)' if avg_score >= 75 else 'var(--yellow)' if avg_score >= 60 else 'var(--red)'}">{avg_score:.0f}<span style="font-size: 1rem; opacity: 0.5">/100</span></div>
            <div class="metric-label">Avg Score</div>
        </div>
        <div class="card">
            <div class="metric-value" style="color: var(--green)">${total_cost:.3f}</div>
            <div class="metric-label">Total Cost</div>
        </div>
        <div class="card">
            <div class="metric-value">{total_tokens:,}</div>
            <div class="metric-label">Tokens Used</div>
        </div>
    </div>

    <div class="section-title">📁 Проекты</div>
    <div class="projects">
        {project_cards}
    </div>

    <div class="section-title">📈 Аналитика</div>
    <div class="charts">
        <div class="chart-container">
            <div class="chart-title">Score Trend</div>
            <canvas id="scoreTrend"></canvas>
        </div>
        <div class="chart-container">
            <div class="chart-title">По проектам</div>
            <canvas id="projectChart"></canvas>
        </div>
        <div class="chart-container">
            <div class="chart-title">По типам</div>
            <canvas id="typeChart"></canvas>
        </div>
    </div>

    <div class="section-title">📋 История Reviews</div>
    <table>
        <thead>
            <tr>
                <th>Дата</th>
                <th>Тип</th>
                <th>Проект</th>
                <th>Score</th>
                <th>Стоимость</th>
                <th>Токены</th>
            </tr>
        </thead>
        <tbody>
            {review_rows}
        </tbody>
    </table>

    <div class="footer">
        METAai v1.2 · Powered by OpenRouter · ${total_cost:.3f} spent · {datetime.now().strftime('%Y-%m-%d')}
    </div>

    <script>
        Chart.defaults.color = '#8888a0';
        Chart.defaults.borderColor = '#2a2a3e';

        // Score Trend
        new Chart(document.getElementById('scoreTrend'), {{
            type: 'line',
            data: {{
                labels: {labels_json},
                datasets: [{{
                    label: 'Score',
                    data: {scores_json},
                    borderColor: '#7c3aed',
                    backgroundColor: 'rgba(124, 58, 237, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#7c3aed',
                    pointRadius: 4,
                }}]
            }},
            options: {{
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ min: 0, max: 100, grid: {{ color: '#1a1a2e' }} }},
                    x: {{ grid: {{ display: false }} }}
                }}
            }}
        }});

        // Project Radar/Bar
        new Chart(document.getElementById('projectChart'), {{
            type: 'doughnut',
            data: {{
                labels: {proj_names},
                datasets: [{{
                    data: {proj_scores},
                    backgroundColor: {proj_colors},
                    borderWidth: 0,
                }}]
            }},
            options: {{
                plugins: {{ legend: {{ position: 'bottom', labels: {{ padding: 15 }} }} }},
                cutout: '60%',
            }}
        }});

        // Type Distribution
        new Chart(document.getElementById('typeChart'), {{
            type: 'bar',
            data: {{
                labels: {type_labels},
                datasets: [{{
                    data: {type_data},
                    backgroundColor: ['#7c3aed', '#06b6d4', '#22c55e', '#eab308'],
                    borderRadius: 8,
                }}]
            }},
            options: {{
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ grid: {{ color: '#1a1a2e' }}, ticks: {{ stepSize: 1 }} }},
                    x: {{ grid: {{ display: false }} }}
                }}
            }}
        }});
    </script>
</body>
</html>"""


def main():
    reviews_dir = Path(__file__).parent / "reviews"
    if not reviews_dir.exists():
        print("📁 Папка reviews/ не найдена")
        return

    data = parse_all_data(reviews_dir)
    html = generate_html(data)

    output = Path(__file__).parent / "dashboard.html"
    output.write_text(html, encoding="utf-8")
    print(f"📊 Dashboard создан: {output}")
    print(f"   Откройте в браузере: file:///{output.as_posix()}")


if __name__ == "__main__":
    main()

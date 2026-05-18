"""
💰 Agent #48: Revenue Tracker
Подключается к CryptoCloud API для реального трекинга платежей.
Работает для ВСЕХ проектов портфеля.

    python -m agents.revenue_tracker               # Показать
    python -m agents.revenue_tracker --save        # + сохранить
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.config import (
    CRYPTOCLOUD_API_KEY_ENV, CRYPTOCLOUD_SHOP_ID_ENV,
    CRYPTOCLOUD_API_URL, REVENUE_CACHE,
    EVOLUTION_DIR, PORTFOLIO,
)


def load_json(path):
    if Path(path).exists():
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def get_creds():
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent.parent / ".env")
    except ImportError:
        pass
    api_key = os.environ.get(CRYPTOCLOUD_API_KEY_ENV, "")
    shop_id = os.environ.get(CRYPTOCLOUD_SHOP_ID_ENV, "")
    return api_key, shop_id


def api_request(api_key, endpoint, params=None):
    """Вызов CryptoCloud API."""
    url = f"{CRYPTOCLOUD_API_URL}/{endpoint}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{qs}"

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except Exception as exc:
        return {"error": str(exc)}


def fetch_invoices(api_key):
    """Получить последние инвойсы из CryptoCloud."""
    data = api_request(api_key, "invoice/merchant/list", {
        "start": 0,
        "limit": 100,
    })

    if data.get("error"):
        return [], data["error"]

    invoices = data.get("result", [])
    return invoices, None


def calculate_revenue(invoices, days=30):
    """Рассчитать revenue за период."""
    cutoff = datetime.now() - timedelta(days=days)
    paid = []

    for inv in invoices:
        if inv.get("status") != "paid":
            continue

        # Parse date
        created = inv.get("created", "")
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if dt.replace(tzinfo=None) >= cutoff:
                amount = float(inv.get("amount_usd", 0) or inv.get("amount", 0))
                paid.append({
                    "date": dt.isoformat(),
                    "amount": amount,
                    "currency": inv.get("currency", "USD"),
                    "order_id": inv.get("order_id", ""),
                })
        except (ValueError, TypeError):
            continue

    total = sum(p["amount"] for p in paid)
    return paid, total


def estimate_mrr(paid_invoices, total_30d):
    """Оценить MRR из платежей."""
    if not paid_invoices:
        return 0

    # Simple: MRR = total_30d (monthly revenue ≈ MRR for subscription models)
    return round(total_30d, 2)


def main():
    args = sys.argv[1:]
    save_md = "--save" in args

    print("\n" + "=" * 60)
    print("  💰 REVENUE TRACKER — Phase 13 Agent #48")
    print("=" * 60)

    api_key, shop_id = get_creds()
    if not api_key:
        print("\n  ⚠️ Нет CryptoCloud API key")
        print(f"  Установи {CRYPTOCLOUD_API_KEY_ENV} в .env")

        # Fallback: show portfolio from config
        print("\n  📊 Портфель (из config):")
        for name, info in PORTFOLIO.items():
            print(f"    {name}: {info['type']} | {info['stage']} | MRR: ${info['mrr']}")

        print("\n" + "=" * 60 + "\n")
        return

    print(f"\n  🔑 API: ...{api_key[-6:]}")
    print(f"  🏪 Shop: {shop_id}")

    # Fetch invoices
    print("\n  🔄 Загружаю инвойсы...")
    invoices, error = fetch_invoices(api_key)

    if error:
        print(f"  ❌ API Error: {error}")
        print("\n" + "=" * 60 + "\n")
        return

    print(f"  📦 Всего инвойсов: {len(invoices)}")

    # Calculate
    paid_30, rev_30 = calculate_revenue(invoices, days=30)
    paid_7, rev_7 = calculate_revenue(invoices, days=7)
    paid_1, rev_1 = calculate_revenue(invoices, days=1)
    mrr = estimate_mrr(paid_30, rev_30)

    # Stats
    total_paid = [i for i in invoices if i.get("status") == "paid"]
    total_pending = [i for i in invoices if i.get("status") == "created"]

    print("\n  📊 Статистика:")
    print(f"    Оплачено: {len(total_paid)} инвойсов")
    print(f"    Pending:  {len(total_pending)} инвойсов")

    print("\n  💰 Revenue:")
    print(f"    24h:  ${rev_1:.2f} ({len(paid_1)} платежей)")
    print(f"    7d:   ${rev_7:.2f} ({len(paid_7)} платежей)")
    print(f"    30d:  ${rev_30:.2f} ({len(paid_30)} платежей)")
    print(f"    MRR:  ${mrr:.2f}")

    # Churn estimate
    if len(total_paid) > 0:
        active_recent = len(paid_30)
        active_prev = len([i for i in invoices if i.get("status") == "paid"]) - active_recent
        if active_prev > 0:
            churn_rate = max(0, 1 - (active_recent / max(active_prev, 1)))
            print(f"    Churn: ~{churn_rate*100:.1f}%")

    # Portfolio update
    results = {
        "timestamp": datetime.now().isoformat(),
        "shop_id": shop_id,
        "total_invoices": len(invoices),
        "total_paid": len(total_paid),
        "total_pending": len(total_pending),
        "revenue_24h": rev_1,
        "revenue_7d": rev_7,
        "revenue_30d": rev_30,
        "mrr": mrr,
        "payments_30d": len(paid_30),
        "projects": {},
    }

    # Map to portfolio projects
    for name, info in PORTFOLIO.items():
        results["projects"][name] = {
            "type": info["type"],
            "stage": info["stage"],
            "mrr": mrr if name == "ONYX" else info.get("mrr", 0),
        }

    if save_md:
        EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
        Path(REVENUE_CACHE).write_text(
            json.dumps(results, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n  💾 Сохранено: {REVENUE_CACHE}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()

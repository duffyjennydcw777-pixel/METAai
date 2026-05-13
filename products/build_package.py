#!/usr/bin/env python3
"""
📦 SoloCTO Prompt Kit — Build & Package Script
Собирает продукт в ZIP-архивы для продажи на Gumroad.

Создаёт 3 тира:
  - solocto-prompt-kit-starter-v1.0.zip   ($9)
  - solocto-prompt-kit-pro-v1.0.zip       ($19)
  - solocto-prompt-kit-team-v1.0.zip      ($49)
"""

import zipfile
from pathlib import Path
from datetime import datetime

VERSION = "1.0"
SRC = Path(__file__).parent / "prompt-kit"
OUT_DIR = Path(__file__).parent / "dist"

TIERS = {
    "starter": {
        "price": "$9",
        "includes": [
            "rules/GLOBAL.md",
            "rules/PROJECT.md",
            "rules/CODE_COMPLEXITY.md",
            "rules/CONVENTIONS.md",
            "rules/MAKER_PROFILE.md",
            "templates/DECISIONS.md",
            "templates/SOLUTION_PATTERNS.md",
            "templates/CHANGELOG.md",
            "setup.py",
            "README.md",
        ],
    },
    "pro": {
        "price": "$19",
        "includes": [
            "rules/GLOBAL.md",
            "rules/PROJECT.md",
            "rules/CODE_COMPLEXITY.md",
            "rules/CONVENTIONS.md",
            "rules/MAKER_PROFILE.md",
            "templates/DECISIONS.md",
            "templates/SOLUTION_PATTERNS.md",
            "templates/CHANGELOG.md",
            "docs/1_PRODUCT.md",
            "docs/2_ARCHITECTURE.md",
            "docs/3_DEPLOYMENT.md",
            "PROMPT_LIBRARY.md",
            "setup.py",
            "README.md",
        ],
    },
    "team": {
        "price": "$49",
        "includes": [
            "rules/GLOBAL.md",
            "rules/PROJECT.md",
            "rules/CODE_COMPLEXITY.md",
            "rules/CONVENTIONS.md",
            "rules/MAKER_PROFILE.md",
            "templates/DECISIONS.md",
            "templates/SOLUTION_PATTERNS.md",
            "templates/CHANGELOG.md",
            "docs/1_PRODUCT.md",
            "docs/2_ARCHITECTURE.md",
            "docs/3_DEPLOYMENT.md",
            "PROMPT_LIBRARY.md",
            "setup.py",
            "README.md",
        ],
    },
}


def build_zip(tier_name: str, tier: dict) -> Path:
    zip_name = f"solocto-prompt-kit-{tier_name}-v{VERSION}.zip"
    zip_path = OUT_DIR / zip_name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        root = f"solocto-prompt-kit-{tier_name}/"

        for rel_path in tier["includes"]:
            src_file = SRC / rel_path
            if not src_file.exists():
                print(f"  ⚠️  Не найден: {rel_path}")
                continue
            arcname = root + rel_path
            zf.write(src_file, arcname)
            print(f"  ✅ {rel_path}")

        # Add tier-specific TEAM_SETUP.md for team tier
        if tier_name == "team":
            team_guide = _generate_team_guide()
            zf.writestr(root + "TEAM_SETUP.md", team_guide)
            print("  ✅ TEAM_SETUP.md (generated)")

        # Add manifest
        manifest = _generate_manifest(tier_name, tier)
        zf.writestr(root + "MANIFEST.txt", manifest)
        print("  ✅ MANIFEST.txt (generated)")

    size_kb = zip_path.stat().st_size // 1024
    return zip_path, size_kb


def _generate_manifest(tier_name: str, tier: dict) -> str:
    now = datetime.now().strftime("%Y-%m-%d")
    files_list = "\n".join(f"  - {f}" for f in tier["includes"])
    return f"""SoloCTO Prompt Kit — {tier_name.upper()} Tier
Version: {VERSION}
Price: {tier['price']}
Built: {now}

Included files:
{files_list}

Quick Start:
  python setup.py /path/to/your/project

Support:
  Open an issue or DM on Gumroad.
  Lifetime updates included.
"""


def _generate_team_guide() -> str:
    return """# 🏢 SoloCTO Prompt Kit — Team Setup Guide

## Multi-Project Setup

### Step 1: Create a shared rules repo
```bash
git init my-team-rules
cd my-team-rules
python setup.py .
```

### Step 2: Customize for your team
Edit `.agent/rules/GLOBAL.md`:
- Add team-specific conventions
- Add your stack-specific rules
- Add project invariants

Edit `.agent/rules/MAKER_PROFILE.md`:
- Replace with team defaults
- Define shared communication style

### Step 3: Per-project setup
In each project, add a `.agent/rules/PROJECT.md` specific to that repo.
Use the template from this kit as a starting point.

### Step 4: Enforce via CI
Add to your CI pipeline:
```yaml
- name: Check AI rules present
  run: |
    test -f .agent/rules/GLOBAL.md || (echo "❌ Rules missing" && exit 1)
    test -f .agent/rules/PROJECT.md || (echo "❌ PROJECT rules missing" && exit 1)
```

## Team Conventions

1. All ADRs go in `DECISIONS.md` — never delete, only append
2. CHANGELOG updated before every merge to main
3. SOLUTION_PATTERNS.md is a team wiki — add patterns as you discover them
4. Code Complexity Level must be stated in every PR description

## Onboarding New Devs
1. Clone rules repo
2. Run `python setup.py /path/to/project`
3. Read `MAKER_PROFILE.md` — customize for yourself
4. Read `CODE_COMPLEXITY.md` — understand the QA levels
5. Done. AI is now calibrated to your team.
"""


def main():
    OUT_DIR.mkdir(exist_ok=True)

    print(f"📦 Building SoloCTO Prompt Kit v{VERSION}")
    print(f"📁 Source: {SRC}")
    print(f"📁 Output: {OUT_DIR}")
    print()

    results = []
    for tier_name, tier in TIERS.items():
        print(f"--- {tier_name.upper()} ({tier['price']}) ---")
        zip_path, size_kb = build_zip(tier_name, tier)
        results.append((tier_name, tier["price"], zip_path.name, size_kb))
        print()

    print("=" * 40)
    print("✅ BUILD COMPLETE")
    print()
    print(f"{'Tier':<10} {'Price':<8} {'File':<45} {'Size'}")
    print("-" * 75)
    for tier_name, price, filename, size_kb in results:
        print(f"{tier_name:<10} {price:<8} {filename:<45} {size_kb} KB")
    print()
    print(f"📂 Output: {OUT_DIR}")
    print()
    print("🚀 Next: Upload to Gumroad")
    print("   1. starter → Product #1 ($9)")
    print("   2. pro     → Product #2 ($19)")
    print("   3. team    → Product #3 ($49)")


if __name__ == "__main__":
    main()

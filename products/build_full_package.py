#!/usr/bin/env python3
"""
📦 Solo CTO OS — Full Product Build Script
Собирает полный продукт в один ZIP для продажи ($249).

Включает:
  - Layer 1: AI Rules (agent-rules/)
  - Layer 2: Multi-Agent Pipeline (agent-pipeline/)
  - Layer 3: Meta-Engineering (ANTI_PATTERNS, CONTEXT_MANIFEST_SPEC)
  - Layer 4: Second Brain Vault (vault/)
  - Getting Started Guide
"""

import zipfile
from pathlib import Path
from datetime import datetime

VERSION = "1.0"
PRODUCT_NAME = "solocto-os"
PRICE = "$249"

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent  # METAai root
SOLOCTO_DIR = SCRIPT_DIR / "solocto-os"
PROMPT_KIT_DIR = SCRIPT_DIR / "prompt-kit"
OUT_DIR = SCRIPT_DIR / "dist"

# Files to EXCLUDE from agent-pipeline (private data, caches)
PIPELINE_EXCLUDE = {
    "__pycache__",
    ".env",
    "reviews",
    "generated_fixes",
    "generated_tests",
    "chat_raw.txt",
    ".git",
    "products",
    "docs",
    ".agent",
    ".github",
}

# Files from METAai root that go into agent-pipeline/
PIPELINE_FILES = [
    "review.py",
    "batch_review.py",
    "entropy.py",
    "impact.py",
    "pareto.py",
    "bayes.py",
    "kolmogorov.py",
    "review_history.py",
    "dashboard.py",
    "dashboard.html",
    "costs.py",
    "fix_tracker.py",
    "watch.py",
    "audit_project.py",
    ".env.example",
    "pyproject.toml",
]

# Agent source files
AGENT_DIR = PROJECT_ROOT / "src" / "agents"


def build_full_package() -> tuple[Path, int]:
    """Build the complete Solo CTO OS ZIP."""
    zip_name = f"{PRODUCT_NAME}-pro-v{VERSION}.zip"
    zip_path = OUT_DIR / zip_name
    root = f"{PRODUCT_NAME}/"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        print("📦 Layer 1: AI Rules (agent-rules/)")
        _add_prompt_kit(zf, root)

        print("\n📦 Layer 2: Multi-Agent Pipeline (agent-pipeline/)")
        _add_pipeline(zf, root)

        print("\n📦 Layer 3: Meta-Engineering")
        _add_meta(zf, root)

        print("\n📦 Layer 4: Second Brain Vault")
        _add_vault(zf, root)

        print("\n📦 Root files")
        _add_root_files(zf, root)

        # Generate manifest
        manifest = _generate_manifest()
        zf.writestr(root + "MANIFEST.txt", manifest)
        print("  ✅ MANIFEST.txt (generated)")

    size_kb = zip_path.stat().st_size // 1024
    return zip_path, size_kb


def _add_prompt_kit(zf: zipfile.ZipFile, root: str):
    """Add Layer 1: Agent Rules from prompt-kit."""
    kit_prefix = root + "agent-rules/"

    # Rules
    rules_dir = PROMPT_KIT_DIR / "rules"
    if rules_dir.exists():
        for f in sorted(rules_dir.iterdir()):
            if f.is_file():
                zf.write(f, kit_prefix + "rules/" + f.name)
                print(f"  ✅ rules/{f.name}")

    # Templates
    templates_dir = PROMPT_KIT_DIR / "templates"
    if templates_dir.exists():
        for f in sorted(templates_dir.iterdir()):
            if f.is_file():
                zf.write(f, kit_prefix + "templates/" + f.name)
                print(f"  ✅ templates/{f.name}")

    # Docs
    docs_dir = PROMPT_KIT_DIR / "docs"
    if docs_dir.exists():
        for f in sorted(docs_dir.iterdir()):
            if f.is_file():
                zf.write(f, kit_prefix + "docs/" + f.name)
                print(f"  ✅ docs/{f.name}")

    # Individual files
    for fname in ["PROMPT_LIBRARY.md", "setup.py", "README.md"]:
        src = PROMPT_KIT_DIR / fname
        if src.exists():
            zf.write(src, kit_prefix + fname)
            print(f"  ✅ {fname}")


def _add_pipeline(zf: zipfile.ZipFile, root: str):
    """Add Layer 2: Multi-Agent Pipeline code."""
    pipe_prefix = root + "agent-pipeline/"

    # Root-level pipeline files
    for fname in PIPELINE_FILES:
        src = PROJECT_ROOT / fname
        if src.exists():
            zf.write(src, pipe_prefix + fname)
            print(f"  ✅ {fname}")
        else:
            print(f"  ⚠️  {fname} — not found")

    # Agent source files
    if AGENT_DIR.exists():
        for f in sorted(AGENT_DIR.iterdir()):
            if f.is_file() and f.suffix == ".py":
                zf.write(f, pipe_prefix + "src/agents/" + f.name)
                print(f"  ✅ src/agents/{f.name}")


def _add_meta(zf: zipfile.ZipFile, root: str):
    """Add Layer 3: Meta-Engineering files."""
    for fname in ["ANTI_PATTERNS.md", "CONTEXT_MANIFEST_SPEC.md"]:
        src = SOLOCTO_DIR / fname
        if src.exists():
            zf.write(src, root + fname)
            print(f"  ✅ {fname}")


def _add_vault(zf: zipfile.ZipFile, root: str):
    """Add Layer 4: Second Brain vault."""
    vault_dir = SOLOCTO_DIR / "vault"
    if not vault_dir.exists():
        print("  ⚠️  vault/ directory not found!")
        return

    vault_prefix = root + "vault/"
    for f in sorted(vault_dir.rglob("*")):
        if f.is_file():
            rel = f.relative_to(vault_dir)
            zf.write(f, vault_prefix + str(rel).replace("\\", "/"))
            print(f"  ✅ vault/{rel}")


def _add_root_files(zf: zipfile.ZipFile, root: str):
    """Add root-level documentation."""
    for fname in ["GETTING_STARTED.md"]:
        src = SOLOCTO_DIR / fname
        if src.exists():
            zf.write(src, root + fname)
            print(f"  ✅ {fname}")


def _generate_manifest() -> str:
    now = datetime.now().strftime("%Y-%m-%d")
    return f"""Solo CTO OS — PRO
Version: {VERSION}
Price: {PRICE}
Built: {now}

What's Inside:
  Layer 1 — AI Rules (agent-rules/)
    5 rule files, 25 prompts, 6 templates, 3 doc templates, setup script

  Layer 2 — Multi-Agent Pipeline (agent-pipeline/)
    10 AI agents, CLI (12 commands), scientific analytics
    Shannon Entropy, Pareto, Bayes, Kolmogorov, Impact Graph

  Layer 3 — Meta-Engineering
    Anti-Patterns Registry (AI immune system)
    Context Manifest Spec (context routing for AI)

  Layer 4 — Second Brain (vault/)
    Obsidian vault template (8 folders)
    Dashboard, Vision, Evolution Log
    Business Metrics, Project MOC, Idea Pipeline
    Life OS templates (idea, quarterly strategy, decision)

Quick Start:
  1. Read GETTING_STARTED.md
  2. Run: python agent-rules/setup.py /your/project
  3. Open vault/ in Obsidian

Support:
  Telegram: @[YOUR_HANDLE]
  Email: [YOUR_EMAIL]
  Lifetime updates included.
"""


def main():
    OUT_DIR.mkdir(exist_ok=True)

    print(f"{'='*50}")
    print(f"📦 Solo CTO OS v{VERSION} — Full Build")
    print(f"💰 Price: {PRICE}")
    print(f"📁 Output: {OUT_DIR}")
    print(f"{'='*50}\n")

    zip_path, size_kb = build_full_package()

    print(f"\n{'='*50}")
    print("✅ BUILD COMPLETE")
    print(f"📄 {zip_path.name}")
    print(f"📊 Size: {size_kb} KB")
    print(f"📂 Path: {zip_path}")
    print(f"{'='*50}")
    print()
    print("🚀 Next steps:")
    print("   1. Review the ZIP contents")
    print("   2. Upload to your sales page")
    print("   3. Share the link")


if __name__ == "__main__":
    main()

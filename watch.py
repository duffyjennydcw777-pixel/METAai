#!/usr/bin/env python3
"""
👁️ METAai Watch Mode
Мониторит файлы и автоматически запускает review при сохранении.

Использование:
    python watch.py --dir C:\\Users\\Gigabyte\\Sylectus\\src --level 2
    python watch.py --dir . --level 2 --pattern "*.py"
"""
import asyncio
import argparse
import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from src.agents.review_agent import ReviewAgent


def get_file_hash(filepath: Path) -> str:
    """Get MD5 hash of file content."""
    try:
        return hashlib.md5(filepath.read_bytes()).hexdigest()
    except Exception:
        return ""


def scan_files(directory: Path, pattern: str = "*.py") -> dict[str, str]:
    """Scan directory and return {path: hash} map."""
    files = {}
    for f in directory.rglob(pattern):
        if any(skip in str(f) for skip in ["__pycache__", ".git", "node_modules", ".venv"]):
            continue
        files[str(f)] = get_file_hash(f)
    return files


async def review_changed_file(filepath: Path, agent: ReviewAgent):
    """Review a single changed file."""
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = len(content.splitlines())

        if lines > 500:
            print(f"   ⏭️ Слишком большой ({lines} строк), пропускаю")
            return

        print(f"   🔍 Reviewing...", end=" ", flush=True)
        response = await agent.review_file(filepath, context="Watch mode auto-review")

        # Extract score
        import re
        score_match = re.search(r"(\d+)/100", response)
        score = int(score_match.group(1)) if score_match else 0

        color = "✅" if score >= 80 else "⚠️" if score >= 60 else "🚫"
        print(f"{color} {score}/100")

        # Print short summary (first verdict line)
        for line in response.splitlines():
            if "Вердикт" in line or "SAFE" in line or "NEEDS" in line or "DO NOT" in line:
                print(f"   → {line.strip()}")
                break

    except Exception as e:
        print(f"   ❌ Ошибка: {e}")


async def watch_loop(directory: Path, pattern: str, level: int, interval: float):
    """Main watch loop."""
    agent = ReviewAgent()
    print(f"\n{'='*60}")
    print(f"👁️  METAai Watch Mode")
    print(f"{'='*60}")
    print(f"📁 Директория: {directory}")
    print(f"🔍 Паттерн:    {pattern}")
    print(f"⏱️  Интервал:    {interval}с")
    print(f"📊 Level:       {level}")
    print(f"\n⏳ Сканирую файлы...")

    # Initial scan
    prev_state = scan_files(directory, pattern)
    print(f"   Найдено {len(prev_state)} файлов")
    print(f"\n👀 Слежу за изменениями... (Ctrl+C для выхода)\n")

    try:
        while True:
            await asyncio.sleep(interval)
            current_state = scan_files(directory, pattern)

            # Find changes
            for filepath, new_hash in current_state.items():
                old_hash = prev_state.get(filepath)

                if old_hash is None:
                    # New file
                    print(f"🆕 Новый файл: {Path(filepath).name}")
                    await review_changed_file(Path(filepath), agent)

                elif old_hash != new_hash:
                    # Modified file
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"📝 [{timestamp}] Изменён: {Path(filepath).name}")
                    await review_changed_file(Path(filepath), agent)

            # Check deleted
            for filepath in prev_state:
                if filepath not in current_state:
                    print(f"🗑️ Удалён: {Path(filepath).name}")

            prev_state = current_state

    except KeyboardInterrupt:
        print(f"\n\n👋 Watch mode остановлен.")


def main():
    parser = argparse.ArgumentParser(description="METAai Watch Mode")
    parser.add_argument("--dir", type=str, required=True, help="Directory to watch")
    parser.add_argument("--level", type=int, default=2, help="Review level")
    parser.add_argument("--pattern", type=str, default="*.py", help="File pattern")
    parser.add_argument("--interval", type=float, default=3.0, help="Scan interval (seconds)")

    args = parser.parse_args()

    directory = Path(args.dir).resolve()
    if not directory.exists():
        print(f"❌ Директория не найдена: {directory}")
        sys.exit(1)

    try:
        asyncio.run(watch_loop(directory, args.pattern, args.level, args.interval))
    except KeyboardInterrupt:
        pass  # Clean exit


if __name__ == "__main__":
    main()

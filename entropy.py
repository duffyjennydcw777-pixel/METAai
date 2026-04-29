"""
📐 Shannon Entropy Analyzer for source code.
Measures code complexity via information entropy.
High entropy = unpredictable, complex code = needs deeper review.

Based on Shannon's Information Theory (1948).
"""
import math
import re
from collections import Counter
from pathlib import Path
from dataclasses import dataclass


@dataclass
class EntropyReport:
    """Entropy analysis result for a file."""
    filepath: str
    char_entropy: float       # Shannon entropy per character
    line_entropy: float       # Entropy of line patterns
    token_entropy: float      # Entropy of code tokens
    complexity_score: float   # Normalized 0-100 score
    recommended_level: int    # 1, 2, or 3
    flags: list               # Why this level was recommended

    def __str__(self) -> str:
        level_emoji = {1: "🟢", 2: "🟡", 3: "🔴"}
        return (
            f"{level_emoji.get(self.recommended_level, '⚪')} "
            f"{Path(self.filepath).name}: "
            f"entropy={self.char_entropy:.2f} bits/char, "
            f"complexity={self.complexity_score:.0f}/100, "
            f"→ Level {self.recommended_level}"
        )


# Keywords that bump complexity regardless of entropy
CRITICAL_PATTERNS = [
    (r'\b(password|secret|token|api_key|private_key)\b', "🔐 Contains secrets/auth"),
    (r'\b(payment|invoice|billing|charge|refund)\b', "💰 Payment logic"),
    (r'\b(exec|eval|subprocess|os\.system)\b', "⚠️ Code execution"),
    (r'\b(sql|query|execute|cursor)\b', "🗄️ Direct SQL"),
    (r'\b(encrypt|decrypt|hash|hmac|cipher)\b', "🔒 Cryptography"),
]


def char_entropy(code: str) -> float:
    """Shannon entropy per character."""
    if not code:
        return 0.0
    freq = Counter(code)
    total = len(code)
    return -sum(
        (count / total) * math.log2(count / total)
        for count in freq.values()
    )


def line_entropy(code: str) -> float:
    """Entropy of line-level patterns (indentation depth, line length)."""
    lines = code.splitlines()
    if not lines:
        return 0.0

    # Measure indentation depths
    depths = []
    for line in lines:
        stripped = line.lstrip()
        if stripped:
            depth = len(line) - len(stripped)
            depths.append(min(depth // 4, 10))  # Normalize to tabs

    if not depths:
        return 0.0

    freq = Counter(depths)
    total = len(depths)
    return -sum(
        (count / total) * math.log2(count / total)
        for count in freq.values()
    )


def token_entropy(code: str) -> float:
    """Entropy of code tokens (identifiers, keywords, operators)."""
    # Simple tokenization: split by non-alphanumeric
    tokens = re.findall(r'[a-zA-Z_]\w*', code)
    if not tokens:
        return 0.0

    freq = Counter(tokens)
    total = len(tokens)
    return -sum(
        (count / total) * math.log2(count / total)
        for count in freq.values()
    )


def analyze_file(filepath: str | Path) -> EntropyReport:
    """Analyze a file and return entropy report with review level recommendation."""
    filepath = Path(filepath)
    code = filepath.read_text(encoding="utf-8", errors="ignore")

    # Calculate entropies
    h_char = char_entropy(code)
    h_line = line_entropy(code)
    h_token = token_entropy(code)

    # Weighted complexity score (0-100)
    # Typical ranges: char=4-5, line=1-3, token=5-10
    complexity = min(100, (
        h_char * 8 +       # char entropy contributes ~32-40
        h_line * 12 +      # line entropy contributes ~12-36
        h_token * 3         # token entropy contributes ~15-30
    ))

    # Check critical patterns
    flags = []
    code_lower = code.lower()
    for pattern, description in CRITICAL_PATTERNS:
        if re.search(pattern, code_lower):
            flags.append(description)

    # Determine review level
    lines_count = len(code.splitlines())

    if flags:
        # Critical patterns → always Level 3
        level = 3
    elif complexity > 75 or lines_count > 500:
        level = 3
    elif complexity > 45 or lines_count > 100:
        level = 2
    else:
        level = 1

    return EntropyReport(
        filepath=str(filepath),
        char_entropy=h_char,
        line_entropy=h_line,
        token_entropy=h_token,
        complexity_score=complexity,
        recommended_level=level,
        flags=flags,
    )


def analyze_directory(directory: str | Path, pattern: str = "*.py") -> list[EntropyReport]:
    """Analyze all matching files in a directory."""
    directory = Path(directory)
    reports = []
    for filepath in sorted(directory.rglob(pattern)):
        # Skip common junk
        if any(skip in str(filepath) for skip in [
            "__pycache__", ".git", "node_modules", ".venv", "venv"
        ]):
            continue
        try:
            report = analyze_file(filepath)
            reports.append(report)
        except Exception:
            continue

    # Sort by complexity (highest first)
    reports.sort(key=lambda r: r.complexity_score, reverse=True)
    return reports


# ── CLI ──────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python entropy.py <file_or_dir> [pattern]")
        print("Example: python entropy.py C:\\Projects\\myapp *.py")
        sys.exit(1)

    target = Path(sys.argv[1])
    pattern = sys.argv[2] if len(sys.argv) > 2 else "*.py"

    print("=" * 60)
    print("📐 Shannon Entropy Analyzer")
    print("=" * 60)

    if target.is_file():
        report = analyze_file(target)
        print(f"\n{report}")
        if report.flags:
            for flag in report.flags:
                print(f"    {flag}")
    elif target.is_dir():
        reports = analyze_directory(target, pattern)
        if not reports:
            print(f"No {pattern} files found in {target}")
            sys.exit(0)

        # Summary
        level_counts = Counter(r.recommended_level for r in reports)
        avg_complexity = sum(r.complexity_score for r in reports) / len(reports)

        print(f"\n📁 {target.name}: {len(reports)} files, "
              f"avg complexity: {avg_complexity:.0f}/100")
        print(f"   🟢 Level 1: {level_counts.get(1, 0)} | "
              f"🟡 Level 2: {level_counts.get(2, 0)} | "
              f"🔴 Level 3: {level_counts.get(3, 0)}")
        print()

        for report in reports:
            print(f"  {report}")
            if report.flags:
                for flag in report.flags:
                    print(f"      {flag}")

    print()
    print("=" * 60)

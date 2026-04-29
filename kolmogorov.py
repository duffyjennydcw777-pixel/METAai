"""
🧬 Kolmogorov Code Smell Detector.
Finds code duplication via normalized compression distance (NCD).
If two files compress well together → they share patterns → likely copy-paste.

Based on Kolmogorov Complexity approximation via zlib compression.
"""
import zlib
from pathlib import Path
from itertools import combinations
from dataclasses import dataclass


@dataclass
class DuplicationPair:
    """A pair of files with suspected code duplication."""
    file_a: str
    file_b: str
    similarity: float   # 0.0 (unrelated) to 1.0 (identical)
    shared_bytes: int    # Estimated shared content size


def normalized_compression_distance(a: bytes, b: bytes) -> float:
    """
    NCD(a, b) = (C(ab) - min(C(a), C(b))) / max(C(a), C(b))
    
    Where C(x) = compressed size of x.
    NCD ≈ 0 means very similar, NCD ≈ 1 means very different.
    """
    if not a or not b:
        return 1.0

    ca = len(zlib.compress(a, 9))
    cb = len(zlib.compress(b, 9))
    cab = len(zlib.compress(a + b, 9))

    ncd = (cab - min(ca, cb)) / max(ca, cb)
    return max(0.0, min(1.0, ncd))


def code_similarity(file_a: Path, file_b: Path) -> float:
    """Calculate similarity between two files (0.0 to 1.0)."""
    a = file_a.read_bytes()
    b = file_b.read_bytes()

    ncd = normalized_compression_distance(a, b)
    # Convert NCD to similarity (1 - ncd)
    return max(0.0, 1.0 - ncd)


def find_duplicates(
    directory: str | Path,
    pattern: str = "*.py",
    threshold: float = 0.45,
    min_size: int = 200,
) -> list[DuplicationPair]:
    """Find suspected code duplications in a directory."""
    directory = Path(directory)

    files = []
    for fp in sorted(directory.rglob(pattern)):
        if any(skip in str(fp) for skip in [
            "__pycache__", ".git", "node_modules", ".venv", "venv",
            "__init__", "test_", "conftest"
        ]):
            continue
        if fp.stat().st_size >= min_size:
            files.append(fp)

    duplicates = []

    for fa, fb in combinations(files, 2):
        sim = code_similarity(fa, fb)
        if sim >= threshold:
            # Estimate shared bytes
            a_size = fa.stat().st_size
            b_size = fb.stat().st_size
            shared = int(min(a_size, b_size) * sim)

            duplicates.append(DuplicationPair(
                file_a=str(fa.relative_to(directory)) if fa.is_relative_to(directory) else fa.name,
                file_b=str(fb.relative_to(directory)) if fb.is_relative_to(directory) else fb.name,
                similarity=sim,
                shared_bytes=shared,
            ))

    # Sort by similarity (highest first)
    duplicates.sort(key=lambda d: d.similarity, reverse=True)
    return duplicates


# ── CLI ──────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python kolmogorov.py <directory> [threshold]")
        print("Example: python kolmogorov.py C:\\Projects\\myapp 0.5")
        sys.exit(1)

    directory = Path(sys.argv[1])
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.45

    print("=" * 60)
    print("🧬 Kolmogorov Code Duplication Detector")
    print(f"   Directory: {directory.name}")
    print(f"   Threshold: {threshold:.0%} similarity")
    print("=" * 60)

    duplicates = find_duplicates(directory, threshold=threshold)

    if not duplicates:
        print(f"\n  ✅ No significant code duplication found (>{threshold:.0%})")
    else:
        print(f"\n  ⚠️ Found {len(duplicates)} suspected duplicate pair(s):\n")
        for dup in duplicates:
            emoji = "🔴" if dup.similarity > 0.7 else "🟡" if dup.similarity > 0.5 else "🟢"
            print(f"  {emoji} {dup.similarity:.0%} similar ({dup.shared_bytes} bytes shared)")
            print(f"      {dup.file_a}")
            print(f"      {dup.file_b}")
            print()

        # Summary
        high = sum(1 for d in duplicates if d.similarity > 0.7)
        med = sum(1 for d in duplicates if 0.5 < d.similarity <= 0.7)
        low = sum(1 for d in duplicates if d.similarity <= 0.5)
        print(f"  Summary: 🔴 {high} high | 🟡 {med} medium | 🟢 {low} low")

    print(f"\n{'=' * 60}")

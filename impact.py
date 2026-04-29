"""
🕸️ Impact Radius — Dependency Graph Analyzer.
Uses import analysis to determine blast radius of code changes.
Graph Theory applied: if you change file X, what else breaks?
"""
import ast
import re
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class ImpactReport:
    """Impact analysis for a changed file."""
    changed_file: str
    direct_dependents: list = field(default_factory=list)     # Files that import this
    indirect_dependents: list = field(default_factory=list)    # 2nd degree
    blast_radius: int = 0                                      # Total affected files
    risk_level: str = "LOW"                                    # LOW/MEDIUM/HIGH/CRITICAL


def extract_imports(filepath: Path) -> set[str]:
    """Extract all imported module names from a Python file."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, Exception):
        # Fallback to regex for broken files
        source = filepath.read_text(encoding="utf-8", errors="ignore")
        imports = set()
        for match in re.finditer(r'^\s*(?:from|import)\s+([a-zA-Z_][\w.]*)', source, re.M):
            module = match.group(1).split('.')[0]
            imports.add(module)
        return imports

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports


def build_dependency_graph(directory: Path, pattern: str = "*.py") -> dict:
    """
    Build a reverse dependency graph.
    graph[module_name] = [list of files that import it]
    """
    # Map: filename (stem) → full path
    file_map = {}
    for fp in directory.rglob(pattern):
        if any(skip in str(fp) for skip in ["__pycache__", ".git", "node_modules", ".venv"]):
            continue
        file_map[fp.stem] = fp

    # Build reverse graph: module → who imports it
    reverse_graph = defaultdict(set)  # module_name → set of importers
    forward_graph = defaultdict(set)  # file → set of modules it imports

    for stem, fp in file_map.items():
        imports = extract_imports(fp)
        for imp in imports:
            if imp in file_map:  # Only track internal imports
                reverse_graph[imp].add(stem)
                forward_graph[stem].add(imp)

    return {
        "reverse": dict(reverse_graph),
        "forward": dict(forward_graph),
        "file_map": file_map,
    }


def analyze_impact(directory: str | Path, changed_file: str, pattern: str = "*.py") -> ImpactReport:
    """Analyze blast radius of changing a specific file."""
    directory = Path(directory)
    changed_stem = Path(changed_file).stem

    graph = build_dependency_graph(directory, pattern)
    reverse = graph["reverse"]
    file_map = graph["file_map"]

    # Direct dependents (1st degree)
    direct = list(reverse.get(changed_stem, set()))

    # Indirect dependents (2nd degree)
    indirect = set()
    for dep in direct:
        for second_deg in reverse.get(dep, set()):
            if second_deg != changed_stem and second_deg not in direct:
                indirect.add(second_deg)

    blast = len(direct) + len(indirect)

    # Risk assessment
    if blast == 0:
        risk = "LOW"
    elif blast <= 3:
        risk = "MEDIUM"
    elif blast <= 8:
        risk = "HIGH"
    else:
        risk = "CRITICAL"

    return ImpactReport(
        changed_file=changed_file,
        direct_dependents=sorted(direct),
        indirect_dependents=sorted(indirect),
        blast_radius=blast,
        risk_level=risk,
    )


def full_graph_report(directory: str | Path, pattern: str = "*.py") -> str:
    """Generate a full dependency report for a project."""
    directory = Path(directory)
    graph = build_dependency_graph(directory, pattern)
    reverse = graph["reverse"]
    forward = graph["forward"]
    file_map = graph["file_map"]

    lines = []
    lines.append("=" * 60)
    lines.append("🕸️ Dependency Graph — Impact Radius")
    lines.append("=" * 60)
    lines.append(f"\n📁 {directory.name}: {len(file_map)} modules\n")

    # Sort by number of dependents (most depended-on first)
    ranked = sorted(reverse.items(), key=lambda x: len(x[1]), reverse=True)

    if not ranked:
        lines.append("  No internal dependencies found.")
        return "\n".join(lines)

    # Hub files (most depended on)
    lines.append("🏗️ Hub files (most depended on):")
    for module, dependents in ranked[:10]:
        dep_count = len(dependents)
        risk = "🔴" if dep_count > 5 else "🟡" if dep_count > 2 else "🟢"
        lines.append(f"  {risk} {module}.py ← {dep_count} files depend on it")
        for d in sorted(dependents)[:5]:
            lines.append(f"      └── {d}.py")
        if len(dependents) > 5:
            lines.append(f"      └── ... +{len(dependents) - 5} more")

    # Leaf files (depend on many, nobody depends on them)
    leaves = set(forward.keys()) - set(reverse.keys())
    if leaves:
        lines.append(f"\n🍃 Leaf files (safe to change, nothing depends on them):")
        for leaf in sorted(leaves):
            imports = forward.get(leaf, set())
            lines.append(f"  🟢 {leaf}.py (imports {len(imports)} modules)")

    # Isolated files
    all_connected = set(forward.keys()) | set(reverse.keys())
    isolated = set(file_map.keys()) - all_connected - {"__init__"}
    if isolated:
        lines.append(f"\n🏝️ Isolated files (no internal deps):")
        for iso in sorted(isolated):
            lines.append(f"  ⚪ {iso}.py")

    lines.append(f"\n{'=' * 60}")
    return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python impact.py <directory>                    # Full graph")
        print("  python impact.py <directory> --file changed.py  # Impact of specific file")
        sys.exit(1)

    directory = Path(sys.argv[1])

    if "--file" in sys.argv:
        idx = sys.argv.index("--file")
        changed = sys.argv[idx + 1]
        report = analyze_impact(directory, changed)
        print(f"🕸️ Impact of changing {report.changed_file}:")
        print(f"   Risk: {report.risk_level} | Blast radius: {report.blast_radius}")
        print(f"   Direct ({len(report.direct_dependents)}): {', '.join(report.direct_dependents)}")
        print(f"   Indirect ({len(report.indirect_dependents)}): {', '.join(report.indirect_dependents)}")
    else:
        print(full_graph_report(directory))

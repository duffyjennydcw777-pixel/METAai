"""
🧪 Smoke tests для METAai CLI.

Минимальный набор: запуск без падений, правильные exit codes, graceful failure.
Запуск: pytest tests/smoke/ -v
"""
import subprocess
import sys
from pathlib import Path

REVIEW_PY = str(Path(__file__).parent.parent.parent / "review.py")
PYTHON = sys.executable


def run_cli(*args, expect_rc=0, timeout=30):
    """Helper: запускает review.py с аргументами, проверяет exit code."""
    cmd = [PYTHON, REVIEW_PY] + list(args)
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout,
        cwd=str(Path(REVIEW_PY).parent)
    )
    if expect_rc is not None:
        assert result.returncode == expect_rc, (
            f"Expected rc={expect_rc}, got {result.returncode}\n"
            f"stdout: {result.stdout[:500]}\n"
            f"stderr: {result.stderr[:500]}"
        )
    return result


class TestCLIHelp:
    """CLI должен показывать help без ошибок."""

    def test_main_help(self):
        r = run_cli("--help")
        assert "METAai" in r.stdout or "review" in r.stdout

    def test_review_help(self):
        r = run_cli("review", "--help")
        assert "--file" in r.stdout
        assert "--level" in r.stdout

    def test_preflight_help(self):
        r = run_cli("preflight", "--help")
        assert "--dir" in r.stdout

    def test_entropy_help(self):
        r = run_cli("entropy", "--help")
        assert "--path" in r.stdout

    def test_impact_help(self):
        r = run_cli("impact", "--help")
        assert "--path" in r.stdout

    def test_pareto_help(self):
        r = run_cli("pareto", "--help")
        assert "pareto" in r.stdout.lower() or "hot" in r.stdout.lower()

    def test_dupes_help(self):
        r = run_cli("dupes", "--help")
        assert "--path" in r.stdout


class TestNoAPIKeyGraceful:
    """Без API ключа CLI должен показать понятную ошибку, а не traceback."""

    def test_review_no_key(self):
        """Review без ключа должен вернуть ошибку конфигурации, не crash."""
        import os
        env = os.environ.copy()
        env.pop("OPENROUTER_API_KEY", None)

        cmd = [PYTHON, REVIEW_PY, "review", "--file", REVIEW_PY]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=15,
            env=env, cwd=str(Path(REVIEW_PY).parent)
        )
        # Должен быть или exit(1) с сообщением, или graceful failure
        # НЕ должен быть traceback
        assert "Traceback" not in result.stderr, (
            f"CLI crashed with traceback:\n{result.stderr[:500]}"
        )


class TestLocalAnalyzers:
    """Анализаторы без API должны работать."""

    def test_entropy_on_self(self):
        """Entropy анализ самого review.py."""
        r = run_cli("entropy", "--path", REVIEW_PY)
        assert "Shannon" in r.stdout or "entropy" in r.stdout.lower() or "Level" in r.stdout

    def test_entropy_on_directory(self):
        """Entropy анализ директории src/agents/."""
        agents_dir = str(Path(REVIEW_PY).parent / "src" / "agents")
        r = run_cli("entropy", "--path", agents_dir)
        assert "Level" in r.stdout or "complexity" in r.stdout.lower()

    def test_impact_on_project(self):
        """Impact graph для проекта."""
        project_dir = str(Path(REVIEW_PY).parent)
        r = run_cli("impact", "--path", project_dir)
        # Должен вернуть хоть что-то
        assert r.returncode == 0

    def test_dupes_on_agents(self):
        """Дупликаты в src/agents/."""
        agents_dir = str(Path(REVIEW_PY).parent / "src" / "agents")
        r = run_cli("dupes", "--path", agents_dir)
        assert "Kolmogorov" in r.stdout or "duplication" in r.stdout.lower() or "✅" in r.stdout


class TestCostsModule:
    """Модуль отслеживания стоимости должен загружаться."""

    def test_costs_import(self):
        cmd = [PYTHON, "-c", "import sys; sys.path.insert(0,'.'); from costs import *; print('OK')"]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10,
            cwd=str(Path(REVIEW_PY).parent)
        )
        assert "OK" in result.stdout


class TestOrchestratorRouting:
    """Базовый тест: orchestrator корректно импортируется и маршрутизирует."""

    def test_orchestrator_import(self):
        cmd = [PYTHON, "-c", """
import sys; sys.path.insert(0,'src')
from agents.orchestrator import AgentOrchestrator
o = AgentOrchestrator()
assert hasattr(o, 'run_pipeline')
assert hasattr(o, 'review_agent')
assert hasattr(o, 'security_agent')
print('OK')
"""]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10,
            cwd=str(Path(REVIEW_PY).parent)
        )
        assert "OK" in result.stdout, f"stderr: {result.stderr[:500]}"

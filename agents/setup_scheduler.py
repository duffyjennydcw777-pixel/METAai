"""
⏰ Настройка автозапуска агентов через Windows Task Scheduler

Создаёт задачу в планировщике:
- Имя: METAai_NightlyAgents
- Время: 23:50 каждый день
- Действие: python -m agents.conductor --save

Использование:
    python agents/setup_scheduler.py          # Создать задачу
    python agents/setup_scheduler.py --remove # Удалить задачу
"""

import subprocess
import sys
from pathlib import Path

TASK_NAME = "METAai_NightlyAgents"
PYTHON_PATH = sys.executable
WORKING_DIR = str(Path(__file__).parent.parent)  # c:\Dev\METAai
SCRIPT_ARGS = "-m agents.conductor --save"
SCHEDULE_TIME = "23:50"


def create_task():
    """Создаёт задачу в Windows Task Scheduler."""
    # Формируем команду schtasks
    cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/TR", f'"{PYTHON_PATH}" {SCRIPT_ARGS}',
        "/SC", "DAILY",
        "/ST", SCHEDULE_TIME,
        "/F",  # Force overwrite if exists
    ]

    print(f"📅 Создаю задачу: {TASK_NAME}")
    print(f"   Время: {SCHEDULE_TIME} каждый день")
    print(f"   Команда: {PYTHON_PATH} {SCRIPT_ARGS}")
    print(f"   Рабочая папка: {WORKING_DIR}")
    print()

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace"
        )
        if result.returncode == 0:
            print("✅ Задача создана!")
            print()
            print("Проверить: schtasks /Query /TN METAai_NightlyAgents")
            print("Запустить вручную: schtasks /Run /TN METAai_NightlyAgents")
        else:
            print(f"❌ Ошибка: {result.stderr}")
            print()
            print("Попробуй запустить от администратора:")
            print(f'  schtasks /Create /TN "{TASK_NAME}" /TR "\\"{PYTHON_PATH}\\" {SCRIPT_ARGS}" /SC DAILY /ST {SCHEDULE_TIME} /F')

    except Exception as e:
        print(f"❌ {e}")


def remove_task():
    """Удаляет задачу из планировщика."""
    cmd = ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace"
        )
        if result.returncode == 0:
            print(f"✅ Задача {TASK_NAME} удалена")
        else:
            print(f"❌ {result.stderr}")
    except Exception as e:
        print(f"❌ {e}")


def main():
    if "--remove" in sys.argv:
        remove_task()
    else:
        create_task()


if __name__ == "__main__":
    main()

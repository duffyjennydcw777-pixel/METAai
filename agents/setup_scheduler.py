"""
⏰ Настройка автозапуска агентов через Windows Task Scheduler

Создаёт задачу в планировщике:
- Имя: METAai_NightlyAgents
- Время: 23:50 каждый день
- Действие: python -m agents.conductor --save
- Рабочая папка: c:\Dev\METAai

Использование:
    python agents/setup_scheduler.py          # Создать задачу
    python agents/setup_scheduler.py --remove # Удалить задачу
    python agents/setup_scheduler.py --status # Проверить статус
"""

import subprocess
import sys
import tempfile
from pathlib import Path

TASK_NAME = "METAai_NightlyAgents"
PYTHON_PATH = sys.executable
WORKING_DIR = str(Path(__file__).parent.parent)  # c:\Dev\METAai
SCRIPT_ARGS = "-m agents.conductor --save"
SCHEDULE_TIME = "23:50"

# XML-шаблон — более надёжный чем schtasks /TR
TASK_XML = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-01-01T{time}:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>{python}</Command>
      <Arguments>{args}</Arguments>
      <WorkingDirectory>{workdir}</WorkingDirectory>
    </Exec>
  </Actions>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT30M</ExecutionTimeLimit>
    <Enabled>true</Enabled>
  </Settings>
</Task>
"""


def create_task():
    """Создаёт задачу в Windows Task Scheduler через XML."""
    xml_content = TASK_XML.format(
        time=SCHEDULE_TIME,
        python=PYTHON_PATH,
        args=SCRIPT_ARGS,
        workdir=WORKING_DIR,
    )

    # Сохраняем XML во временный файл
    xml_path = Path(WORKING_DIR) / "agents" / "_task_schedule.xml"
    xml_path.write_text(xml_content, encoding="utf-16")

    print(f"📅 Создаю задачу: {TASK_NAME}")
    print(f"   Время: {SCHEDULE_TIME} каждый день")
    print(f"   Python: {PYTHON_PATH}")
    print(f"   Команда: python {SCRIPT_ARGS}")
    print(f"   Рабочая папка: {WORKING_DIR}")
    print()

    cmd = [
        "schtasks", "/Create",
        "/TN", TASK_NAME,
        "/XML", str(xml_path),
        "/F",  # Force overwrite
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace"
        )
        if result.returncode == 0:
            print("✅ Задача создана!")
            print()
            print("Команды:")
            print(f"  Проверить: schtasks /Query /TN {TASK_NAME}")
            print(f"  Запустить: schtasks /Run /TN {TASK_NAME}")
            print(f"  Удалить:   python agents/setup_scheduler.py --remove")
        else:
            print(f"❌ Ошибка: {result.stderr}")
            if "Access" in result.stderr or "доступ" in result.stderr.lower():
                print()
                print("⚠️  Запусти от администратора:")
                print(f'  schtasks /Create /TN "{TASK_NAME}" /XML "{xml_path}" /F')

    except Exception as e:
        print(f"❌ {e}")
    finally:
        # Убираем временный XML
        if xml_path.exists():
            xml_path.unlink()


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


def check_status():
    """Проверяет статус задачи."""
    cmd = ["schtasks", "/Query", "/TN", TASK_NAME, "/FO", "LIST", "/V"]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace"
        )
        if result.returncode == 0:
            print(f"📋 Задача: {TASK_NAME}")
            print(result.stdout)
        else:
            print(f"❌ Задача не найдена: {result.stderr.strip()}")
    except Exception as e:
        print(f"❌ {e}")


def main():
    if "--remove" in sys.argv:
        remove_task()
    elif "--status" in sys.argv:
        check_status()
    else:
        create_task()


if __name__ == "__main__":
    main()

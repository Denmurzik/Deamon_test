"""
CLI-валидатор курса для GitHub Actions.

Использование:
    python -m src.validate Example
    python -m src.validate /path/to/course_dir

Выход: 0 если валидация прошла, 1 если есть ошибки.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Импорт валидатора
try:
    from .course_validator import validate_course
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from course_validator import validate_course


def collect_files(course_root: Path) -> set:
    """Собрать все файлы в директории курса (относительные пути)."""
    result = set()
    for root, _, filenames in os.walk(course_root):
        for fn in filenames:
            full = Path(root) / fn
            rel = str(full.relative_to(course_root)).replace("\\", "/")
            result.add(rel)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Валидация курса перед импортом")
    parser.add_argument("path", type=Path, help="Путь к директории курса")
    args = parser.parse_args()

    course_path = args.path
    if not course_path.exists() or not course_path.is_dir():
        print(f"ОШИБКА: {course_path} не существует или не директория")
        sys.exit(1)

    # Найти course.json
    json_file = None
    for name in ("course.json", "course.backend.json"):
        candidate = course_path / name
        if candidate.exists():
            json_file = candidate
            break

    if not json_file:
        print(f"ОШИБКА: course.json не найден в {course_path}")
        sys.exit(1)

    # Парсинг JSON
    try:
        data = json.loads(json_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ОШИБКА: не удалось прочитать {json_file}: {e}")
        sys.exit(1)

    # Сбор файлов
    available_files = collect_files(course_path)
    # Убираем course.json из списка
    available_files.discard(json_file.name)

    title = data.get("title") or data.get("course_name") or "?"
    print(f"🔍 Валидация курса: {title}")
    print(f"   JSON: {json_file.name}")
    print(f"   Файлов: {len(available_files)}")
    print()

    # Валидация
    result = validate_course(data, available_files)

    # Вывод результатов
    if result.warnings:
        for w in result.warnings:
            print(f"  ⚠️  {w}")
        print()

    if result.errors:
        for e in result.errors:
            print(f"  ❌ {e}")
        print()
        print(f"❌ Валидация провалена: {len(result.errors)} ошибок, {len(result.warnings)} предупреждений")
        sys.exit(1)
    else:
        print(f"✅ Валидация пройдена ({len(result.warnings)} предупреждений)")
        sys.exit(0)


if __name__ == "__main__":
    main()

"""
Валидатор курса для импорта в NSUTS.

Проверяет course.json на корректность ПЕРЕД отправкой в NSUTS,
чтобы не создавать мусорные олимпиады из-за сломанных данных.

Pydantic-free — работает и в demon, и в Deamon_test (GitHub Actions).

Использование:
    from course_validator import validate_course

    result = validate_course(course_dict, available_files)
    if not result.is_valid:
        print("Ошибки:", result.errors)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any

# NSUTS _checkParams regex для title олимпиады
# Perl: /^([\w\sа-яА-Я_-]*)$/
# Разрешены: буквы (лат/кир), цифры, пробел, _, -
_NSUTS_TITLE_RE = re.compile(r'^[\w\sа-яА-ЯёЁ_-]+$')

# NSUTS _checkParams regex для address_name
# Perl: /^\s*([a-zA-Z_0-9]+)\s*$/
_NSUTS_ADDRESS_RE = re.compile(r'^[a-zA-Z0-9_]+$')


@dataclass
class ValidationResult:
    """Результат валидации курса."""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def validate_course(
    data: Dict[str, Any],
    available_files: Optional[Set[str]] = None,
) -> ValidationResult:
    """Валидирует структуру курса перед импортом.

    Args:
        data: распарсенный JSON курса (dict).
        available_files: множество доступных файлов (relative paths).
            Если None — проверка существования файлов пропускается.

    Returns:
        ValidationResult с errors (блокируют импорт) и warnings.
    """
    r = ValidationResult()
    files = available_files or set()

    # === Course level ===
    title = data.get("title") or data.get("course_name") or ""
    if not title.strip():
        r.error("course.title — обязательное поле, не может быть пустым")
    elif not _NSUTS_TITLE_RE.match(title):
        r.warn(
            f"course.title содержит спецсимволы: {title!r}. "
            "Будет санитайзен (: . / и др. заменены на -)"
        )

    address = data.get("address_name") or ""
    if not address.strip():
        r.error("course.address_name — обязательное поле для создания олимпиады в NSUTS")
    elif not _NSUTS_ADDRESS_RE.match(address):
        r.error(
            f"course.address_name={address!r} — недопустимые символы. "
            "Разрешены только латинские буквы, цифры и _ (regex: [a-zA-Z0-9_]+)"
        )

    modules = data.get("modules")
    if not modules or not isinstance(modules, list):
        r.error("course.modules — обязательный непустой список")
        return r  # дальше проверять нечего

    # === Module level ===
    for mi, mod in enumerate(modules):
        prefix = f"modules[{mi}]"

        mod_title = mod.get("title") or mod.get("module_name") or ""
        if not mod_title.strip():
            r.error(f"{prefix}.title — обязательное поле")

        # content может быть в ключе "content" или "submodules"
        content = mod.get("content") or mod.get("submodules") or []
        if not isinstance(content, list):
            r.error(f"{prefix}.content — должен быть списком")
            continue

        if not content:
            r.warn(f"{prefix} — пустой модуль (нет задач)")

        # === Content item level ===
        for ci, item in enumerate(content):
            item_prefix = f"{prefix}.content[{ci}]"

            # Если элемент содержит вложенные tasks[] (новый формат)
            if "tasks" in item and isinstance(item.get("tasks"), list):
                _validate_submodule_with_tasks(
                    r, item, item_prefix, files,
                )
                continue

            _validate_content_item(r, item, item_prefix, files)

    return r


def _validate_content_item(
    r: ValidationResult,
    item: Dict[str, Any],
    prefix: str,
    files: Set[str],
) -> None:
    """Валидирует отдельный content item (task или submodule)."""
    item_title = item.get("title") or item.get("task_name") or item.get("submodule_name") or ""
    if not item_title.strip():
        r.error(f"{prefix}.title — обязательное поле")

    # contentUrl — проверка существования файла
    content_url = item.get("contentUrl")
    if content_url and files and content_url not in files:
        r.error(f"{prefix}.contentUrl={content_url!r} — файл не найден")

    # testsUrl — проверка паритета .in/.out
    tests_url = item.get("testsUrl")
    if tests_url and files:
        _validate_tests(r, tests_url, prefix, files)

    # time_limit — парсинг
    tl = item.get("time_limit")
    if tl is not None:
        if not _parse_time_limit(str(tl)):
            r.warn(f"{prefix}.time_limit={tl!r} — не удалось распарсить, будет 1с")

    # memory_limit — парсинг
    ml = item.get("memory_limit")
    if ml is not None:
        if not _parse_memory_limit(str(ml)):
            r.warn(f"{prefix}.memory_limit={ml!r} — не удалось распарсить, будет 256MB")


def _validate_submodule_with_tasks(
    r: ValidationResult,
    item: Dict[str, Any],
    prefix: str,
    files: Set[str],
) -> None:
    """Валидирует submodule с вложенными tasks[]."""
    sub_title = item.get("title") or ""
    if not sub_title.strip():
        r.error(f"{prefix}.title — обязательное поле")

    content_url = item.get("contentUrl")
    if content_url and files and content_url not in files:
        r.error(f"{prefix}.contentUrl={content_url!r} — файл не найден")

    tasks = item.get("tasks", [])
    for ti, task in enumerate(tasks):
        _validate_content_item(r, task, f"{prefix}.tasks[{ti}]", files)


def _validate_tests(
    r: ValidationResult,
    tests_url: str,
    prefix: str,
    files: Set[str],
) -> None:
    """Проверяет что тесты имеют парные .in/.out файлы."""
    tests_prefix = tests_url.rstrip("/") + "/"
    test_files = {f for f in files if f.startswith(tests_prefix)}

    if not test_files:
        r.error(f"{prefix}.testsUrl={tests_url!r} — нет тестовых файлов")
        return

    in_files = set()
    out_files = set()
    for f in test_files:
        basename = f[len(tests_prefix):]  # e.g. "1.in"
        if basename.endswith(".in"):
            in_files.add(basename[:-3])
        elif basename.endswith(".out"):
            out_files.add(basename[:-4])

    missing_out = in_files - out_files
    missing_in = out_files - in_files

    if missing_out:
        r.error(
            f"{prefix}.testsUrl={tests_url!r} — отсутствуют .out файлы "
            f"для тестов: {sorted(missing_out)}"
        )
    if missing_in:
        r.error(
            f"{prefix}.testsUrl={tests_url!r} — отсутствуют .in файлы "
            f"для тестов: {sorted(missing_in)}"
        )

    if not in_files and not out_files:
        r.warn(
            f"{prefix}.testsUrl={tests_url!r} — файлы есть, "
            "но нет .in/.out пар"
        )


def _parse_time_limit(s: str) -> bool:
    """Проверяет что time_limit парсится корректно."""
    s = s.strip().lower()
    if s.endswith("ms"):
        s = s[:-2]
    elif s.endswith("s"):
        s = s[:-1]
    try:
        float(s)
        return True
    except ValueError:
        return False


def _parse_memory_limit(s: str) -> bool:
    """Проверяет что memory_limit парсится корректно."""
    s = s.strip().upper()
    for suffix in ("MB", "M", "KB", "K"):
        if s.endswith(suffix):
            s = s[: -len(suffix)].strip()
            break
    try:
        float(s)
        return True
    except ValueError:
        return False

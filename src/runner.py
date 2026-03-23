from __future__ import annotations

import argparse
import os
import sys
import json
from pathlib import Path

# Импорты внутри пакета
try:
    from .parser import parse_course_archive
    from .client import CourseUploader, APIClientError
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from parser import parse_course_archive
    from client import CourseUploader, APIClientError


def run(path: Path, url: str | None, token: str | None, dry_run: bool) -> None:
    # ... (проверки пути)

    print(f"📦 Parsing course from: {path}...")
    try:
        # 1. Парсинг
        course_data = parse_course_archive(path)
        print(f"✅ Parsed successfully: '{course_data.get('title')}' "
              f"({len(course_data.get('modules', []))} modules)")

        # 2. Dry Run
        if dry_run or not (url and token):
            print("\n👀 Dry Run / No Credentials. JSON Output:")
            print(json.dumps(course_data, ensure_ascii=False, indent=2))
            return

        # 3. Отправка (передаем path для сбора файлов)
        print(f"\n🚀 Uploading to {url}...")
        uploader = CourseUploader(base_url=url, api_token=token)

        # ВНИМАНИЕ: теперь передаем еще и path
        uploader.upload_course(course_data, course_root=path)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse and upload course from directory.")

    parser.add_argument("path", type=Path, help="Path to course directory (unpacked)")

    parser.add_argument("--url", type=str, default=os.getenv("LMS_API_URL"),
                        help="LMS API URL (or set LMS_API_URL env var)")

    parser.add_argument("--token", type=str, default=os.getenv("LMS_API_TOKEN"),
                        help="LMS API Token (or set LMS_API_TOKEN env var)")

    parser.add_argument("--dry-run", action="store_true",
                        help="Print JSON to stdout instead of uploading")

    args = parser.parse_args()

    if not args.dry_run and (not args.url or not args.token):
        print("⚠️ Warning: --url and --token are required for upload. "
              "Running in dry-run mode (printing JSON).")

    run(args.path, args.url, args.token, args.dry_run)
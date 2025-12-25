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
    """
    Main logic: parse directory and optionally upload.
    """
    if not path.exists():
        print(f"❌ Error: Path not found: {path}")
        sys.exit(1)

    if not path.is_dir():
        print(f"❌ Error: Path is not a directory: {path}")
        sys.exit(1)

    print(f"📦 Parsing course from: {path}...")
    try:
        # 1. Парсинг (теперь принимает папку)
        course_data = parse_course_archive(path)
        print(f"✅ Parsed successfully: '{course_data.get('course_name')}' "
              f"({len(course_data.get('modules', []))} modules)")

        # 2. Dry Run / Output
        if dry_run or not (url and token):
            print("\n👀 Dry Run / No Credentials provided. JSON Output:")
            print("-" * 40)
            print(json.dumps(course_data, ensure_ascii=False, indent=2))
            print("-" * 40)
            return

        # 3. Отправка на сервер
        print(f"\n🚀 Uploading to {url}...")
        uploader = CourseUploader(base_url=url, api_token=token)
        payload_str = json.dumps(course_data, ensure_ascii=False)
        print(f"ℹ️ Payload size: {len(payload_str) / 1024 / 1024:.2f} MB")
        uploader.upload_course(course_data)

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
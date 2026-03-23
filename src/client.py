import os
import requests
import json
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Any, Dict, List
from .exceptions import APIClientError


class CourseUploader:
    def __init__(self, base_url: str, api_token: str, timeout: int = 120, max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # X-API-Key — сервер использует ApiKeyAuthAttribute с заголовком X-API-Key
        # Content-Type для multipart выставлять вручную НЕ НАДО (requests сделает это сам)
        self.session.headers.update({
            "X-API-Key": api_token,
            "User-Agent": "CourseParser/1.1"
        })
        # Self-signed сертификат на сервере — отключаем проверку
        self.session.verify = False

    def upload_course(self, course_data: Dict[str, Any], course_root: Path) -> None:
        endpoint = f"{self.base_url}/api/v1/courses/import"

        # 1. Собираем файлы для отправки
        files_payload = []

        # JSON передаем как поле формы, а не как body
        # Важно: ensure_ascii=False, чтобы кириллица не ломалась
        payload = {
            "course_json": json.dumps(course_data, ensure_ascii=False)
        }

        print(f"📦 Collecting files from {course_root}...")

        # Рекурсивный обход папки
        file_count = 0
        try:
            for root, _, filenames in os.walk(course_root):
                for filename in filenames:
                    # Пропускаем служебные файлы и бинарники
                    if filename.startswith('.') or filename.startswith('__'):
                        continue
                    ext = Path(filename).suffix.lower()
                    if ext in {'.exe', '.dll', '.so', '.o', '.class', '.pyc'}:
                        continue

                    file_path = Path(root) / filename

                    # Вычисляем относительный путь, чтобы сохранить структуру на сервере
                    # Например: modules/Mod1/Task1/image.png
                    relative_path = file_path.relative_to(course_root)

                    # Открываем файл в бинарном режиме
                    # requests автоматически закроет файлы, если использовать контекст, но здесь список.
                    # Requests поддерживает список кортежей ('field_name', (filename, file_obj))
                    # Мы передаем relative_path как filename
                    files_payload.append(
                        ('files', (str(relative_path).replace("\\", "/"), open(file_path, 'rb')))
                    )
                    file_count += 1

            print(f"📡 Uploading {file_count} files + JSON to {endpoint}...")

            # 2. Отправка (multipart/form-data)
            # При передаче files=... requests сам ставит Content-Type: multipart/form-data
            response = self.session.post(
                endpoint,
                data=payload,
                files=files_payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            print(f"✅ Upload successful. Server Response: {response.text}")

        except Exception as e:
            raise APIClientError(f"Upload failed: {str(e)}")
        finally:
            # Хорошим тоном будет закрыть открытые дескрипторы
            for _, (_, f_obj) in files_payload:
                f_obj.close()
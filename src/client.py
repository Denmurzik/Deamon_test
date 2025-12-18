import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Any, Dict
from .exceptions import APIClientError


class CourseUploader:
    """Client for uploading parsed course data with robust retry logic."""

    def __init__(self, base_url: str, api_token: str, timeout: int = 30, max_retries: int = 3):
        """
        Initialize the uploader.

        Args:
            base_url: Root URL of the API.
            api_token: Authorization token.
            timeout: Socket timeout in seconds.
            max_retries: How many times to retry on failure.
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

        # Retry strategy: wait 1s, 2s, 4s on 429/5xx errors
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "User-Agent": "CourseParser/1.0"
        })

    def upload_course(self, course_data: Dict[str, Any]) -> None:
        """
        Send course data to the server with auto-retry.
        """
        endpoint = f"{self.base_url}/api/v1/courses/import"

        try:
            response = self.session.post(
                endpoint,
                json=course_data,
                timeout=self.timeout
            )
            response.raise_for_status()

            print(f"✅ Course uploaded successfully. Server Status: {response.status_code}")

        except requests.exceptions.RetryError:
            raise APIClientError(f"Failed to upload after maximum retries to {endpoint}")
        except requests.exceptions.ConnectionError:
            raise APIClientError(f"Connection failed (check internet or URL): {self.base_url}")
        except requests.exceptions.HTTPError as e:
            body = ""
            try:
                body = e.response.text
            except Exception:
                body = "<unreadable response body>"
            raise APIClientError(
                f"Server refused data (Status {e.response.status_code}): {body}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise APIClientError(f"Request failed: {str(e)}") from e
        except Exception as e:
            raise APIClientError(f"Unexpected upload error: {str(e)}") from e
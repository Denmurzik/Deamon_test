import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Any, Dict
from .exceptions import APIClientError


class CourseUploader:
    """Client for uploading parsed course data with robust retry logic."""

    # INCREASED TIMEOUT to 120s to handle large zip processing on the server
    def __init__(self, base_url: str, api_token: str, timeout: int = 120, max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

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
        # Ensure we don't accidentally double-slash if the base_url was set improperly
        endpoint = f"{self.base_url}/api/v1/courses/import"

        try:
            print(f"📡 POSTing to {endpoint} (Timeout: {self.timeout}s)...")
            response = self.session.post(
                endpoint,
                json=course_data,
                timeout=self.timeout
            )
            response.raise_for_status()

            print(f"✅ Course uploaded successfully. Server Status: {response.status_code}")

        except requests.exceptions.RetryError as e:
            # IMPROVED ERROR LOGGING: Attempts to show the underlying cause
            error_msg = f"Failed to upload after maximum retries to {endpoint}."
            if e.last_response is not None:
                error_msg += f" Last Status: {e.last_response.status_code}"
            raise APIClientError(error_msg) from e

        except requests.exceptions.ConnectionError:
            raise APIClientError(f"Connection failed (check internet or URL): {self.base_url}")

        except requests.exceptions.HTTPError as e:
            body = e.response.text if e.response else "<no body>"
            raise APIClientError(
                f"Server refused data (Status {e.response.status_code}): {body}"
            ) from e

        except requests.exceptions.Timeout:
            raise APIClientError(f"Request timed out after {self.timeout} seconds.")

        except Exception as e:
            raise APIClientError(f"Unexpected upload error: {str(e)}") from e
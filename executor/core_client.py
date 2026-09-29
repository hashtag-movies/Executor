"""Small HTTP client for a future/actual Hashtag-core deployment."""
import requests

class CoreClient:
    def __init__(self, base_url: str, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def register_body(self, manifest: dict) -> dict:
        r = requests.post(f"{self.base_url}/v1/bodies/register", json=manifest, timeout=self.timeout)
        r.raise_for_status(); return r.json()

    def report_result(self, result: dict) -> dict:
        r = requests.post(f"{self.base_url}/v1/body/result", json=result, timeout=self.timeout)
        r.raise_for_status(); return r.json()

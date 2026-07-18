from typing import Any
import httpx
from core.settings import settings
from providers.base import ProviderAPIError, ProviderConfigurationError


class ForeplayClient:
    def __init__(self) -> None:
        self.base_url = settings.foreplay_base_url.rstrip("/")
        self.api_key = settings.foreplay_api_key

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self.configured:
            raise ProviderConfigurationError("FOREPLAY_API_KEY is not configured.")

        try:
            response = httpx.get(
                f"{self.base_url}/{path.lstrip('/')}",
                headers={
                    "Authorization": self.api_key,
                    "Accept": "application/json",
                },
                params=params,
                timeout=45,
            )
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPError as exc:
            raise ProviderAPIError(f"Foreplay request failed: {exc}") from exc

        if not isinstance(payload, dict):
            raise ProviderAPIError("Foreplay returned an unexpected response.")
        return payload

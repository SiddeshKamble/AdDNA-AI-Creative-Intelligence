from typing import Any
import httpx
from core.settings import settings
from providers.base import ProviderAPIError, ProviderConfigurationError


class PiPiSpyClient:
    def __init__(self) -> None:
        self.base_url = settings.pipispy_base_url.rstrip("/")
        self.endpoint = settings.pipispy_endpoint
        self.api_key = settings.pipispy_api_key

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def post_operation(
        self,
        *,
        uri: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        if not self.configured:
            raise ProviderConfigurationError("PIPISPY_API_KEY is not configured.")

        payload = {
            "key": self.api_key,
            "uri": uri,
            "params": params,
        }

        try:
            response = httpx.post(
                f"{self.base_url}/{self.endpoint.lstrip('/')}",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json=payload,
                timeout=45,
            )
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPError as exc:
            raise ProviderAPIError(f"PiPiSpy request failed: {exc}") from exc

        if not isinstance(body, dict):
            raise ProviderAPIError("PiPiSpy returned an unexpected response.")
        if body.get("code") not in (None, 200) or body.get("success") is False:
            raise ProviderAPIError(
                f"PiPiSpy error: {body.get('message', 'Unknown error')}"
            )
        return body

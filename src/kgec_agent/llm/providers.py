"""Provider-neutral orchestration with offline fixture and live structured paths."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

from pydantic import AnyHttpUrl, BaseModel, SecretStr, ValidationError

from kgec_agent.schemas.models import (
    ExplanationOutput,
    LLMStructuredResponse,
    ScenarioFixture,
)


class LLMProviderError(RuntimeError):
    pass


class LLMProviderConfigurationError(LLMProviderError):
    pass


class LLMProviderResponseError(LLMProviderError):
    pass


class FixtureLLMProvider:
    """Frozen reviewed structured response used by every offline replay."""

    def __init__(self, fixture: ScenarioFixture) -> None:
        self.fixture = fixture

    def map_request(self, natural_language_request: str) -> LLMStructuredResponse:
        if " ".join(natural_language_request.split()) != " ".join(
            self.fixture.natural_language_request.split()
        ):
            raise LLMProviderResponseError(
                "offline fixture mode accepts the reviewed scenario request only"
            )
        return self.fixture.llm.model_copy(deep=True)

    def explain(self, recorded_outputs: dict[str, Any]) -> str:
        required = {"scenario_id", "initial_route", "evidence", "final_decision", "destination"}
        if set(recorded_outputs) != required:
            raise ValueError("explanation input must contain only the recorded public fields")
        return (
            f"{recorded_outputs['scenario_id']} routed to "
            f"{recorded_outputs['initial_route']}; evidence was "
            f"{recorded_outputs['evidence']}. The recorded final decision is "
            f"{recorded_outputs['final_decision']} and the destination is "
            f"{recorded_outputs['destination']}."
        )


class LiveLLMConfig(BaseModel):
    endpoint_url: AnyHttpUrl
    model: str
    api_key: SecretStr
    timeout_seconds: float = 20.0

    @classmethod
    def from_environment(cls) -> "LiveLLMConfig":
        required = {
            "endpoint_url": os.getenv("KGEC_LLM_ENDPOINT"),
            "model": os.getenv("KGEC_LLM_MODEL"),
            "api_key": os.getenv("KGEC_LLM_API_KEY"),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise LLMProviderConfigurationError(
                "missing live-provider settings: " + ", ".join(sorted(missing))
            )
        timeout = float(os.getenv("KGEC_LLM_TIMEOUT_SECONDS", "20"))
        return cls(**required, timeout_seconds=timeout)


Transport = Callable[[urllib.request.Request, float], bytes]


def _default_transport(request: urllib.request.Request, timeout: float) -> bytes:
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


class LiveStructuredLLMProvider:
    """OpenAI-compatible structured-output path, instantiated only by explicit selection."""

    def __init__(self, config: LiveLLMConfig, transport: Transport | None = None) -> None:
        self.config = config
        self.transport = transport or _default_transport

    def _request(self, messages: list[dict[str, str]], schema: type[BaseModel]) -> BaseModel:
        payload = {
            "model": self.config.model,
            "temperature": 0,
            "messages": messages,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__,
                    "strict": True,
                    "schema": schema.model_json_schema(),
                },
            },
        }
        request = urllib.request.Request(
            str(self.config.endpoint_url),
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.api_key.get_secret_value()}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            raw = self.transport(request, self.config.timeout_seconds)
            response = json.loads(raw.decode("utf-8"))
            content = response["choices"][0]["message"]["content"]
            document = content if isinstance(content, dict) else json.loads(content)
            return schema.model_validate(document)
        except (TimeoutError, urllib.error.URLError, OSError) as exc:
            raise LLMProviderError("live structured provider unavailable") from exc
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
            KeyError,
            IndexError,
            TypeError,
            ValidationError,
        ) as exc:
            raise LLMProviderResponseError("invalid structured provider response") from exc

    def map_request(self, natural_language_request: str) -> LLMStructuredResponse:
        return self._request(
            [
                {
                    "role": "system",
                    "content": (
                        "Map the request to the validated link-prediction query and the "
                        "canonical eight-tool plan. Do not estimate confidence or decide admission."
                    ),
                },
                {"role": "user", "content": natural_language_request},
            ],
            LLMStructuredResponse,
        )

    def explain(self, recorded_outputs: dict[str, Any]) -> str:
        response = self._request(
            [
                {
                    "role": "system",
                    "content": (
                        "Explain only the supplied recorded tool outputs. Return an explanation "
                        "field and do not propose replacements for any system result."
                    ),
                },
                {"role": "user", "content": json.dumps(recorded_outputs, sort_keys=True)},
            ],
            ExplanationOutput,
        )
        return response.explanation

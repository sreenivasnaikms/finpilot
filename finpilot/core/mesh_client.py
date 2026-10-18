"""Mesh API Client (Mandatory Hackathon Sponsor Gateway).

All LLM/AI calls in FinPilot route strictly through Mesh API using the OpenAI SDK.
Base URL: https://api.meshapi.ai/v1
Key prefix: rsk_
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from finpilot.config import settings

logger = logging.getLogger("finpilot.mesh_client")


class MeshAPIClient:
    """Gateway client for Mesh API routing."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("MESH_API_KEY") or settings.MESH_API_KEY
        self.base_url = base_url or os.getenv("MESH_BASE_URL") or settings.MESH_BASE_URL or "https://api.meshapi.ai/v1"
        
        # Initialize OpenAI client pointing to Mesh API
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key or "rsk_placeholder_for_local_eval"
        )
        self.default_model = settings.DEFAULT_MODEL

    def is_configured(self) -> bool:
        """Returns True if a real Mesh API key is provided."""
        return bool(self.api_key and self.api_key.startswith("rsk_"))

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        json_mode: bool = False,
        fallback_response: Optional[str] = None,
    ) -> str:
        """Execute chat completion routed through Mesh API."""
        target_model = model or self.default_model
        
        try:
            kwargs: Dict[str, Any] = {
                "model": target_model,
                "messages": messages,
                "temperature": temperature,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            return content or ""
        except Exception as e:
            logger.warning(f"Mesh API call failed: {e}. Checking fallback.")
            if fallback_response is not None:
                return fallback_response
            raise e

    def json_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.1,
        fallback_dict: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute chat completion and parse JSON result."""
        raw_text = ""
        try:
            raw_text = self.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                json_mode=True,
                fallback_response=json.dumps(fallback_dict) if fallback_dict else None,
            )
            # Clean markdown code blocks if present
            cleaned = raw_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except Exception as e:
            logger.error(f"Failed to parse JSON response: {e}. Raw text was: {raw_text}")
            if fallback_dict is not None:
                return fallback_dict
            raise e


# Singleton instance
_mesh_client_instance: Optional[MeshAPIClient] = None


def get_mesh_client() -> MeshAPIClient:
    """Retrieve or create the singleton Mesh API client."""
    global _mesh_client_instance
    if _mesh_client_instance is None:
        _mesh_client_instance = MeshAPIClient()
    return _mesh_client_instance

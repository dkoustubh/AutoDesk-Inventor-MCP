"""
OmniCAD Model Router & LLM Provider Abstraction
Manages Gemma 31B (96 GB VRAM local server 192.168.11.86) and optional Mistral review.
"""
import os
import httpx
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        pass

class GemmaLocalProvider(LLMProvider):
    """
    Primary local reasoning engine hosted on 192.168.11.86 (Gemma 31B via vLLM).
    """
    def __init__(self, api_base: Optional[str] = None):
        self.api_base = (api_base or settings.VLLM_API_BASE).rstrip("/")
        self.model = settings.VLLM_MODEL

    async def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        url = f"{self.api_base}/chat/completions"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.1,
                    "max_tokens": 1024
                })
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"[GemmaLocal] vLLM request returned {res.status_code}: {res.text}")
                    return ""
        except Exception as e:
            logger.warning(f"[GemmaLocal] Could not reach local vLLM server: {e}")
            return ""

class MistralAPIProvider(LLMProvider):
    """
    Secondary cloud reviewer for complex or high-risk mechanical validation.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY", "")
        self.api_url = "https://api.mistral.ai/v1/chat/completions"

    async def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            return ""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    self.api_url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": "mistral-large-latest",
                        "messages": messages,
                        "temperature": 0.1
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"[MistralAPI] Mistral API request failed: {e}")
        return ""

class ModelRouter:
    """
    Intelligent router selecting the optimal reasoning model and review strategy.
    """
    def __init__(self):
        self.gemma = GemmaLocalProvider()
        self.mistral = MistralAPIProvider()

    def route_request(self, prompt: str, is_complex: bool = False, requires_review: bool = False) -> LLMProvider:
        if requires_review and self.mistral.api_key:
            logger.info("[ModelRouter] Routing to Mistral Reviewer for complex verification")
            return self.mistral
        logger.info("[ModelRouter] Routing to primary Gemma 31B local engine")
        return self.gemma

"""Thin OpenRouter client for narrative synthesis.

The app is fully functional WITHOUT an API key - every number and framework is
computed deterministically offline. The LLM only turns that structured analysis
into a board-ready narrative. Bring your own key via the OPENROUTER_API_KEY
environment variable (see .env.example).
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from . import config

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMUnavailable(RuntimeError):
    """Raised when no key is configured or the request library is missing."""


def is_configured() -> bool:
    return bool(config.get_openrouter_key())


def generate(prompt: str,
             system: Optional[str] = None,
             model: Optional[str] = None,
             temperature: float = 0.3,
             max_tokens: int = 1600) -> str:
    """Call OpenRouter chat completions and return the text response."""
    key = config.get_openrouter_key()
    if not key:
        raise LLMUnavailable("OPENROUTER_API_KEY is not set.")

    try:
        import requests  # imported lazily so offline use needs no dependency
    except ImportError as exc:  # pragma: no cover
        raise LLMUnavailable("The 'requests' package is required for LLM calls.") from exc

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model or config.DEFAULT_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "X-Title": "Kisunla Launch Strategist",
    }
    resp = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload), timeout=90)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def generate_briefing(context: Dict[str, Any], model: Optional[str] = None) -> str:
    """Produce the executive launch briefing from the framework context."""
    prompt = (
        "Using ONLY the structured launch analysis below, write a concise, board-ready "
        "Go/No-Go briefing for the US launch of Kisunla (donanemab) in early symptomatic "
        "Alzheimer's disease. Structure it as: (1) Recommendation & rationale, "
        "(2) Market & competitive position, (3) Access & payer strategy, "
        "(4) Financial outlook (label all figures as modelled), (5) Top risks & mitigations, "
        "(6) Conditions to proceed. Keep it under ~600 words. Do not invent numbers.\n\n"
        f"STRUCTURED ANALYSIS (JSON):\n{json.dumps(context, indent=2, default=str)}"
    )
    return generate(prompt, system=config.LLM_SYSTEM_GUARDRAIL, model=model)

"""Kisunla (donanemab) Launch Strategist - internal decision-support engine.

Public API:
    build_analysis(overrides)  -> pure, offline framework analysis
    build_briefing(overrides)  -> analysis + narrative (LLM optional)
"""
from .synthesis import build_analysis, build_briefing, deterministic_briefing  # noqa: F401

__all__ = ["build_analysis", "build_briefing", "deterministic_briefing"]
__version__ = "1.0.0"

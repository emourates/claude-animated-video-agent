"""Storyboard generation with Claude, plus loading hand-written storyboards."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from app.config import settings

STORYBOARD_SCHEMA = """{
  "title": "short title",
  "caption": "social caption without hashtags",
  "hashtags": ["#tag1", "#tag2"],
  "scenes": [
    {
      "duration": 3,
      "media": "file name from the media list, or null for a plain background",
      "media_start": 0,
      "text": "short on-screen headline",
      "subtext": "optional second line",
      "text_position": "top | center | bottom"
    }
  ]
}"""


def load_storyboard(path: Path) -> Dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not data.get("scenes"):
        raise ValueError(f"Storyboard {path} has no scenes")
    return data


def _extract_json(text: str) -> Dict[str, Any]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("Claude did not return a JSON storyboard")
    return json.loads(match.group(0))


def generate_storyboard(prompt: str, media_files: List[str] | None = None) -> Dict[str, Any]:
    """Ask Claude for a storyboard. Needs ANTHROPIC_API_KEY."""
    if not settings.ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to .env, or pass --storyboard with a JSON file."
        )
    import anthropic  # imported lazily so --storyboard works without the SDK

    media_note = (
        "Available raw media files (use their exact names in `media`):\n- " + "\n- ".join(media_files)
        if media_files
        else "No raw media is available; set `media` to null."
    )
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=2000,
        system=(
            "You write storyboards for vertical 9:16 social videos (Reels, TikTok, Shorts). "
            "Keep on-screen text short. Never invent numbers, prices or customer projects. "
            "Answer with JSON only, matching this schema:\n" + STORYBOARD_SCHEMA
        ),
        messages=[{"role": "user", "content": f"{prompt}\n\n{media_note}"}],
    )
    text = "".join(block.text for block in message.content if getattr(block, "type", "") == "text")
    return _extract_json(text)


__all__ = ["generate_storyboard", "load_storyboard", "STORYBOARD_SCHEMA"]

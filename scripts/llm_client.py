from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

GEMINI_MODEL_ALIASES = {
    "flash": os.environ.get("GEMINI_FLASH_MODEL", "gemini-2.5-flash"),
    "pro": os.environ.get("GEMINI_PRO_MODEL", "gemini-2.5-pro"),
}


def resolve_custom_api_key(value: str | None) -> str | None:
    return value or os.environ.get("OPENAI_API_KEY") or os.environ.get("CUSTOM_API_KEY")


def resolve_custom_base_url(value: str | None) -> str | None:
    return value or os.environ.get("OPENAI_BASE_URL") or os.environ.get("CUSTOM_BASE_URL")


def normalize_chat_completions_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return base + "/chat/completions"


def custom_chat_completion(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    images: list[str] | None = None,
    temperature: float = 0.2,
    timeout: int = 300,
) -> str:
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for image_path in images or []:
        path = Path(image_path)
        suffix = path.suffix.lower()
        mime = "image/jpeg"
        if suffix == ".png":
            mime = "image/png"
        elif suffix == ".webp":
            mime = "image/webp"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        content.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}})

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": temperature,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        normalize_chat_completions_url(base_url),
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")[-1200:]
        raise RuntimeError(f"Custom API HTTP {exc.code}: {detail}") from exc

    try:
        message = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected custom API response: {json.dumps(data, ensure_ascii=False)[:1200]}") from exc

    if isinstance(message, list):
        parts = []
        for item in message:
            if isinstance(item, dict):
                parts.append(item.get("text") or item.get("content") or "")
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(message or "")

#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["google-genai>=1.0.0"]
# ///
"""分析文章/Markdown/网页文本，输出电商爆款图文拆解。"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.request
from pathlib import Path
from llm_client import custom_chat_completion, resolve_custom_api_key, resolve_custom_base_url

MODEL_ALIASES = {"flash": os.environ.get("GEMINI_FLASH_MODEL", "gemini-2.5-flash"), "pro": os.environ.get("GEMINI_PRO_MODEL", "gemini-2.5-pro")}
DEFAULT_PROMPT = """
你是资深电商内容策划。请分析下面这篇文章/图文/广告文案，目标是提取可复用结构，并为自家电商产品再创作做准备。

重要原则：只提取结构和表达方式，不复制原品牌、原素材、原独特文案。

请用中文输出，并严格包含：

# 爆款图文内容拆解报告

## 1. 基础信息
- 内容类型：文章/广告/种草/测评/教程/案例
- 目标用户：
- 核心情绪：
- 转化目标：

## 2. 标题/开头钩子
- 标题结构：
- 开头如何抓人：
- 使用的钩子类型：痛点/反常识/悬念/利益/数据/场景
- 钩子强度评分：1-10

## 3. 正文结构
- 第一部分：
- 第二部分：
- 第三部分：
- 结尾：

## 4. 可转成短视频的场景
| 段落/观点 | 可视化画面 | 适合镜头 | 可用旁白 |
|---|---|---|---|

## 5. 可复制元素
- 钩子句式：
- 论证顺序：
- 场景表达：
- 情绪触发：
- CTA方式：

## 6. 不可复制/风险元素
- 原品牌/专有内容：
- 原文独特表达：
- 版权/合规风险：

## 7. 再创作建议
- 适合替换的产品类型：
- 适合替换的用户痛点：
- 建议保留的结构：
- 建议重写的内容：
""".strip()


def get_api_key(value: str | None) -> str | None:
    return value or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def read_source(input_path: str | None, url: str | None) -> str:
    if input_path:
        return Path(input_path).expanduser().read_text(encoding="utf-8", errors="ignore")
    if url:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    raise ValueError("Either --input or --url is required")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze ecommerce viral article/text with Gemini")
    parser.add_argument("--input", "-i", default=None)
    parser.add_argument("--url", default=None)
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--provider", choices=["gemini", "custom"], default="gemini", help="LLM provider: gemini or OpenAI-compatible custom API")
    parser.add_argument("--model", choices=["flash", "pro"], default="flash")
    parser.add_argument("--model-id", default=None, help="Exact model id. For custom provider this is required unless CUSTOM_MODEL is set.")
    parser.add_argument("--base-url", default=None, help="OpenAI-compatible API base URL, e.g. https://example.com/v1")
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args()

    source = read_source(args.input, args.url)
    if len(source) > 120000:
        source = source[:120000]

    prompt = f"{args.prompt}\n\n--- 原始内容开始 ---\n{source}\n--- 原始内容结束 ---"

    if args.provider == "custom":
        api_key = resolve_custom_api_key(args.api_key)
        base_url = resolve_custom_base_url(args.base_url)
        model_id = args.model_id or os.environ.get("CUSTOM_MODEL")
        if not api_key or not base_url or not model_id:
            print("Missing custom provider config. Need --base-url, --api-key, --model-id (or env CUSTOM_BASE_URL/CUSTOM_API_KEY/CUSTOM_MODEL).", file=sys.stderr)
            sys.exit(1)
        print(f"Analyzing text with custom model {model_id} at {base_url}...", file=sys.stderr)
        text = custom_chat_completion(base_url=base_url, api_key=api_key, model=model_id, prompt=prompt)
    else:
        api_key = get_api_key(args.api_key)
        if not api_key:
            print("Missing API key. Set GEMINI_API_KEY or GOOGLE_API_KEY.", file=sys.stderr)
            sys.exit(1)
        from google import genai
        client = genai.Client(api_key=api_key)
        model_id = args.model_id or MODEL_ALIASES[args.model]
        print(f"Analyzing text with {model_id}...", file=sys.stderr)
        response = client.models.generate_content(model=model_id, contents=prompt)
        text = response.text or ""
    if args.output:
        out = Path(args.output).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"Saved: {out}", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()

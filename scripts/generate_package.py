#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["google-genai>=1.0.0", "pyyaml>=6.0.0"]
# ///
"""基于爆款分析结果 + 产品brief，生成完整电商再创作方案。"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from llm_client import custom_chat_completion, resolve_custom_api_key, resolve_custom_base_url

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
MODEL_ALIASES = {"flash": os.environ.get("GEMINI_FLASH_MODEL", "gemini-2.5-flash"), "pro": os.environ.get("GEMINI_PRO_MODEL", "gemini-2.5-pro")}


def get_api_key(value: str | None) -> str | None:
    return value or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def read_many(paths: list[str]) -> str:
    chunks = []
    for item in paths:
        path = Path(item).expanduser().resolve()
        chunks.append(f"\n\n--- 文件：{path.name} ---\n" + path.read_text(encoding="utf-8", errors="ignore"))
    return "".join(chunks)


def build_prompt(analysis_text: str, product_text: str, duration: int, platform: str) -> str:
    framework = (SKILL_DIR / "references" / "analysis-framework.md").read_text(encoding="utf-8")
    formulas = (SKILL_DIR / "references" / "viral-formulas.md").read_text(encoding="utf-8")
    platform_notes = (SKILL_DIR / "references" / "platform-notes.md").read_text(encoding="utf-8")
    return f"""
你是资深跨境电商短视频创意总监。请基于爆款内容分析和自家产品资料，生成一份完整的原创宣传视频再创作方案。

核心原则：
- 只复用爆款结构，不复制原素材、原品牌、原人物、原字幕、原音乐、原画面。
- 输出必须可执行，能交给拍摄、剪辑或视频生成模型使用。
- 每个卖点都要有画面证明，不要只写抽象文案。
- 避免绝对化用语和无法证明的承诺。

目标平台：{platform}
目标时长：{duration} 秒

# 参考分析框架
{framework}

# 爆款公式库
{formulas}

# 平台适配
{platform_notes}

# 爆款内容分析结果
{analysis_text}

# 自家产品资料
{product_text}

请输出以下完整结构：

# 电商爆款内容再创作方案

## 1. 原爆款内容拆解摘要
- 爆点是什么
- 前3秒为什么有效
- 最值得复用的结构
- 必须规避的风险

## 2. 可复用爆款公式
- 钩子公式
- 叙事公式
- 节奏公式
- 转化公式

## 3. 自家产品卖点映射表
| 爆款元素 | 原内容表达 | 自家产品替换 | 画面证明 | 备注 |
|---|---|---|---|---|

## 4. 原创宣传脚本
按时间段输出，每段包含：旁白/字幕、画面、目的。

## 5. 短视频分镜表
| 镜号 | 时间 | 景别 | 画面内容 | 旁白/字幕 | 运镜/转场 | 素材要求 |
|---|---|---|---|---|---|---|

## 6. 视频生成提示词
输出一个可直接复制到 Seedance/Veo/Runway/可灵 的中文提示词。必须包含主体、动作、环境、风格、镜头、禁用内容、声音建议。

## 7. 素材补拍清单
按产品素材、场景素材、证明素材分类。

## 8. QA检查表
包含爆款复用、产品表达、转化、合规、专项产品细节检查。
""".strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ecommerce viral remix package")
    parser.add_argument("--analysis", "-a", nargs="+", required=True)
    parser.add_argument("--product", "-p", required=True)
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--platform", default="TikTok/Reels/Shorts/独立站")
    parser.add_argument("--provider", choices=["gemini", "custom"], default="gemini")
    parser.add_argument("--model", choices=["flash", "pro"], default="pro")
    parser.add_argument("--model-id", default=None, help="Exact model id. For custom provider this is required unless CUSTOM_MODEL is set.")
    parser.add_argument("--base-url", default=None, help="OpenAI-compatible API base URL")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--prompt-only", action="store_true")
    args = parser.parse_args()

    prompt = build_prompt(read_many(args.analysis), Path(args.product).expanduser().read_text(encoding="utf-8", errors="ignore"), args.duration, args.platform)
    out = Path(args.output).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.prompt_only:
        out.write_text(prompt, encoding="utf-8")
        print(f"Prompt saved: {out}", file=sys.stderr)
        return

    if args.provider == "custom":
        api_key = resolve_custom_api_key(args.api_key)
        base_url = resolve_custom_base_url(args.base_url)
        model_id = args.model_id or os.environ.get("CUSTOM_MODEL")
        if not api_key or not base_url or not model_id:
            print("Missing custom provider config. Need --base-url, --api-key, --model-id (or env CUSTOM_BASE_URL/CUSTOM_API_KEY/CUSTOM_MODEL), or use --prompt-only.", file=sys.stderr)
            sys.exit(1)
        print(f"Generating package with custom model {model_id} at {base_url}...", file=sys.stderr)
        text = custom_chat_completion(base_url=base_url, api_key=api_key, model=model_id, prompt=prompt)
    else:
        api_key = get_api_key(args.api_key)
        if not api_key:
            print("Missing API key. Set GEMINI_API_KEY or GOOGLE_API_KEY, or use --prompt-only.", file=sys.stderr)
            sys.exit(1)
        from google import genai
        client = genai.Client(api_key=api_key)
        model_id = args.model_id or MODEL_ALIASES[args.model]
        print(f"Generating package with {model_id}...", file=sys.stderr)
        response = client.models.generate_content(model=model_id, contents=prompt)
        text = response.text or ""
    out.write_text(text, encoding="utf-8")
    print(f"Saved: {out}", file=sys.stderr)


if __name__ == "__main__":
    main()

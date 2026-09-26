#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["google-genai>=1.0.0"]
# ///
"""用 Gemini 分析短视频，输出结构化爆款拆解。"""
from __future__ import annotations

import argparse
import os
import sys
import subprocess
import time
from pathlib import Path
from llm_client import custom_chat_completion, resolve_custom_api_key, resolve_custom_base_url

MODEL_ALIASES = {"flash": os.environ.get("GEMINI_FLASH_MODEL", "gemini-2.5-flash"), "pro": os.environ.get("GEMINI_PRO_MODEL", "gemini-2.5-pro")}
RESOLUTION_ALIASES = {"low": "media_resolution_low", "medium": "media_resolution_medium", "high": "media_resolution_high"}

DEFAULT_PROMPT = """
你是资深电商短视频广告分析师。请对这个爆款视频做结构化拆解，目标是后续为自家产品做原创再创作。

重要原则：只提取可复用结构，不建议复制原素材、原品牌、原人物、原字幕、原音乐或原画面。

请用中文输出，并严格包含以下部分：

# 爆款视频拆解报告

## 1. 基础信息
- 内容类型：广告/种草/测评/剧情/教程/对比
- 推测目标用户：
- 推测转化目标：
- 视频整体风格：

## 2. 前3秒钩子
- 第0秒第一帧：
- 文案钩子：
- 视觉钩子：
- 声音/BGM/音效：
- 文案与画面的配合：
- 钩子强度评分：1-10，并说明原因

## 3. 分镜结构
| 时间 | 景别 | 画面内容 | 字幕/旁白 | 转场/节奏 | 目的 |
|---|---|---|---|---|---|

## 4. 节奏与视觉
- 剪辑节奏：
- 色调/滤镜：
- 字幕样式：
- 产品展示方式：
- 记忆点：

## 5. 转化设计
- 痛点如何建立：
- 产品/方案如何出现：
- 信任如何建立：
- 结果如何证明：
- CTA 如何出现：

## 6. 可复制元素
- 钩子句式：
- 叙事结构：
- 分镜节奏：
- 视觉风格：
- CTA方式：

## 7. 不可复制/风险元素
- 原品牌/Logo：
- 原人物/达人：
- 原字幕/音乐/画面：
- 侵权或平台风险：
- 合规风险：

## 8. 可改造成电商宣传片的方向
- 适合替换的产品类型：
- 适合替换的用户痛点：
- 建议保留的结构：
- 建议重写的部分：
""".strip()


def get_api_key(value: str | None) -> str | None:
    return value or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def is_url(value: str) -> bool:
    return value.startswith(("http://", "https://"))


def upload_and_wait(client, file_path: str):
    print(f"Uploading: {file_path}", file=sys.stderr)
    uploaded = client.files.upload(file=file_path)
    while uploaded.state and uploaded.state.name != "ACTIVE":
        print(f"Processing: {uploaded.state.name}", file=sys.stderr)
        time.sleep(4)
        uploaded = client.files.get(name=uploaded.name)
    return uploaded


def extract_keyframes(video_path: Path, output_dir: Path, frames: int) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pattern = output_dir / "frame-%03d.jpg"
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vf", f"fps=1/{max(frames, 1)},scale=768:-1",
        "-frames:v", str(frames),
        str(pattern),
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError("ffmpeg not found. Install with: brew install ffmpeg") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError((exc.stderr or exc.stdout)[-1200:]) from exc
    return [str(path) for path in sorted(output_dir.glob("frame-*.jpg"))]


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze ecommerce viral video with Gemini")
    parser.add_argument("--video", "-v", required=True)
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--prompt", "-p", default=None)
    parser.add_argument("--prompt-file", default=None)
    parser.add_argument("--provider", choices=["gemini", "custom"], default="gemini", help="gemini uses native video; custom uses keyframes via OpenAI-compatible vision chat")
    parser.add_argument("--model", choices=["flash", "pro"], default="flash")
    parser.add_argument("--model-id", default=None, help="Exact model id. For custom provider this is required unless CUSTOM_MODEL is set.")
    parser.add_argument("--base-url", default=None, help="OpenAI-compatible API base URL")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--resolution", choices=["low", "medium", "high"], default="medium")
    parser.add_argument("--keyframes", type=int, default=12, help="Number of keyframes to send for custom provider")
    args = parser.parse_args()

    prompt = Path(args.prompt_file).read_text(encoding="utf-8") if args.prompt_file else (args.prompt or DEFAULT_PROMPT)

    if args.provider == "custom":
        api_key = resolve_custom_api_key(args.api_key)
        base_url = resolve_custom_base_url(args.base_url)
        model_id = args.model_id or os.environ.get("CUSTOM_MODEL")
        if not api_key or not base_url or not model_id:
            print("Missing custom provider config. Need --base-url, --api-key, --model-id (or env CUSTOM_BASE_URL/CUSTOM_API_KEY/CUSTOM_MODEL).", file=sys.stderr)
            sys.exit(1)
        if is_url(args.video):
            prompt = prompt + f"\n\n视频链接：{args.video}\n如果你无法直接访问链接，请基于链接上下文说明需要用户提供本地视频或截图。"
            images = []
        else:
            video_path = Path(args.video).expanduser().resolve()
            if not video_path.exists():
                print(f"Video not found: {video_path}", file=sys.stderr)
                sys.exit(1)
            frame_dir = (Path(args.output).expanduser().resolve().parent if args.output else video_path.parent) / f"{video_path.stem}-keyframes"
            images = extract_keyframes(video_path, frame_dir, args.keyframes)
            prompt = prompt + "\n\n我已从视频中按时间顺序抽取关键帧。请结合这些关键帧推断视频分镜、节奏、视觉钩子和转化逻辑。"
        print(f"Analyzing video with custom model {model_id} at {base_url}...", file=sys.stderr)
        text = custom_chat_completion(base_url=base_url, api_key=api_key, model=model_id, prompt=prompt, images=images)
        if args.output:
            out = Path(args.output).expanduser().resolve()
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
            print(f"Saved: {out}", file=sys.stderr)
        else:
            print(text)
        return

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Missing API key. Set GEMINI_API_KEY or GOOGLE_API_KEY.", file=sys.stderr)
        sys.exit(1)

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    model_id = args.model_id or MODEL_ALIASES[args.model]
    config = types.GenerateContentConfig(media_resolution=RESOLUTION_ALIASES[args.resolution])
    parts = []

    if is_url(args.video):
        parts.append(types.Part(file_data=types.FileData(file_uri=args.video)))
    else:
        video_path = Path(args.video).expanduser().resolve()
        if not video_path.exists():
            print(f"Video not found: {video_path}", file=sys.stderr)
            sys.exit(1)
        size_mb = video_path.stat().st_size / 1024 / 1024
        if size_mb <= 20:
            mime = {".webm": "video/webm", ".mov": "video/quicktime"}.get(video_path.suffix.lower(), "video/mp4")
            parts.append(types.Part(inline_data=types.Blob(data=video_path.read_bytes(), mime_type=mime)))
        else:
            uploaded = upload_and_wait(client, str(video_path))
            parts.append(types.Part(file_data=types.FileData(file_uri=uploaded.uri)))

    parts.append(types.Part(text=prompt))
    print(f"Analyzing with {model_id}...", file=sys.stderr)
    response = client.models.generate_content(model=model_id, contents=types.Content(parts=parts), config=config)
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

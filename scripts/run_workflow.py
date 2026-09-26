#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["google-genai>=1.0.0", "pyyaml>=6.0.0"]
# ///
"""一键执行电商爆款内容再创作工作流。"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    print("\n$ " + " ".join(cmd), file=sys.stderr)
    subprocess.run(cmd, check=True)


def load_downloaded_videos(manifest_path: Path) -> list[str]:
    if not manifest_path.exists():
        return []
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    videos = []
    for item in data.get("results", []):
        videos.extend(item.get("media_files", []))
    return [v for v in videos if Path(v).suffix.lower() != ".mp3"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full ecommerce viral remix workflow")
    parser.add_argument("--urls", nargs="*", default=[])
    parser.add_argument("--videos", nargs="*", default=[])
    parser.add_argument("--texts", nargs="*", default=[])
    parser.add_argument("--product", required=True)
    parser.add_argument("--workdir", default="_temp/ecommerce-remix")
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--platform", default="TikTok/Reels/Shorts/独立站")
    parser.add_argument("--provider", choices=["gemini", "custom"], default="gemini")
    parser.add_argument("--model", choices=["flash", "pro"], default="flash")
    parser.add_argument("--final-model", choices=["flash", "pro"], default="pro")
    parser.add_argument("--model-id", default=None, help="Exact model id for custom provider or Gemini override")
    parser.add_argument("--final-model-id", default=None, help="Exact final generation model id")
    parser.add_argument("--base-url", default=None, help="OpenAI-compatible API base URL for custom provider")
    parser.add_argument("--api-key", default=None, help="API key for selected provider")
    parser.add_argument("--cookies-browser", default="chrome")
    parser.add_argument("--prompt-only", action="store_true")
    args = parser.parse_args()

    workdir = Path(args.workdir).expanduser().resolve()
    input_dir = workdir / "inputs"
    analysis_dir = workdir / "analysis"
    final_dir = workdir / "final"
    for folder in [input_dir, analysis_dir, final_dir]:
        folder.mkdir(parents=True, exist_ok=True)

    videos = [str(Path(v).expanduser().resolve()) for v in args.videos]
    if args.urls:
        run([sys.executable, str(SCRIPT_DIR / "download_media.py"), "--urls", *args.urls, "--output-dir", str(input_dir), "--cookies-browser", args.cookies_browser])
        videos.extend(load_downloaded_videos(input_dir / "download-manifest.json"))

    analysis_files: list[str] = []
    for idx, video in enumerate(videos, 1):
        out = analysis_dir / f"video-analysis-{idx:02d}.md"
        if args.prompt_only:
            source = Path(video).expanduser().resolve()
            out.write_text(
                f"# 待分析视频素材\n\n原始视频文件：{source}\n\n说明：当前为 prompt-only 模式，未调用模型分析视频。请在最终生成提示词中把该视频作为待拆解素材处理。\n",
                encoding="utf-8",
            )
        else:
            cmd = [sys.executable, str(SCRIPT_DIR / "analyze_video.py"), "--video", video, "--output", str(out), "--provider", args.provider, "--model", args.model]
            if args.model_id:
                cmd += ["--model-id", args.model_id]
            if args.base_url:
                cmd += ["--base-url", args.base_url]
            if args.api_key:
                cmd += ["--api-key", args.api_key]
            run(cmd)
        analysis_files.append(str(out))

    for idx, text_path in enumerate(args.texts, 1):
        out = analysis_dir / f"text-analysis-{idx:02d}.md"
        source = Path(text_path).expanduser().resolve()
        if args.prompt_only:
            content = source.read_text(encoding="utf-8", errors="ignore")
            out.write_text(
                f"# 待分析文本素材\n\n原始文件：{source}\n\n说明：当前为 prompt-only 模式，未调用模型分析文本。以下为原始爆款素材内容，供最终生成提示词使用。\n\n---\n\n{content}\n",
                encoding="utf-8",
            )
        else:
            cmd = [sys.executable, str(SCRIPT_DIR / "analyze_text.py"), "--input", str(source), "--output", str(out), "--provider", args.provider, "--model", args.model]
            if args.model_id:
                cmd += ["--model-id", args.model_id]
            if args.base_url:
                cmd += ["--base-url", args.base_url]
            if args.api_key:
                cmd += ["--api-key", args.api_key]
            run(cmd)
        analysis_files.append(str(out))

    if not analysis_files:
        print("No analysis files generated. Provide --urls, --videos, or --texts.", file=sys.stderr)
        sys.exit(1)

    final_output = final_dir / "ecommerce-viral-remix-package.md"
    cmd = [sys.executable, str(SCRIPT_DIR / "generate_package.py"), "--analysis", *analysis_files, "--product", str(Path(args.product).expanduser().resolve()), "--output", str(final_output), "--duration", str(args.duration), "--platform", args.platform, "--provider", args.provider, "--model", args.final_model]
    final_model_id = args.final_model_id or args.model_id
    if final_model_id:
        cmd += ["--model-id", final_model_id]
    if args.base_url:
        cmd += ["--base-url", args.base_url]
    if args.api_key:
        cmd += ["--api-key", args.api_key]
    if args.prompt_only:
        cmd.append("--prompt-only")
    run(cmd)
    print(f"\nDONE: {final_output}")


if __name__ == "__main__":
    main()

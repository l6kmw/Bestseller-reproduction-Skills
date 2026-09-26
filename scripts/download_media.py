#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""多平台爆款视频/音频下载工具。依赖 yt-dlp。"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

URL_RE = re.compile(r"https?://[^\s'\"<>]+")
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv", ".flv", ".avi", ".m4v"}


def extract_urls(values: list[str]) -> list[str]:
    urls: list[str] = []
    for value in values:
        if value.startswith(("http://", "https://")):
            urls.append(value.strip())
        else:
            urls.extend(match.rstrip("，。),]") for match in URL_RE.findall(value))
    result, seen = [], set()
    for url in urls:
        if url not in seen:
            seen.add(url)
            result.append(url)
    return result


def platform_name(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "douyin" in host:
        return "douyin"
    if "tiktok" in host:
        return "tiktok"
    if "youtube" in host or "youtu.be" in host:
        return "youtube"
    if "instagram" in host:
        return "instagram"
    if "xiaohongshu" in host or "xhslink" in host:
        return "xiaohongshu"
    return re.sub(r"[^a-z0-9]+", "-", host).strip("-") or "media"


def clear_proxy_for_cn_sites(url: str) -> list[str]:
    if not any(domain in url for domain in ["douyin.com", "xiaohongshu.com", "xhslink.com"]):
        return []
    cleared = []
    for key in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"]:
        if key in os.environ:
            del os.environ[key]
            cleared.append(key)
    return cleared


def run_ytdlp(url: str, output_dir: Path, index: int, cookies_browser: str | None, audio_only: bool) -> dict:
    platform = platform_name(url)
    output_template = str(output_dir / f"{index:02d}-{platform}-%(id)s.%(ext)s")
    cmd = ["yt-dlp", "--no-warnings", "--no-check-certificates", "--write-info-json", "--write-thumbnail", "--output", output_template]
    if cookies_browser:
        cmd += ["--cookies-from-browser", cookies_browser]
    if platform in {"douyin", "xiaohongshu"}:
        cmd += ["--proxy", ""]
    if audio_only:
        cmd += ["--extract-audio", "--audio-format", "mp3"]
    else:
        cmd += ["--format", "bv*+ba/best"]
    cmd.append(url)

    before = {p.name for p in output_dir.iterdir()} if output_dir.exists() else set()
    cleared = clear_proxy_for_cn_sites(url)
    if cleared:
        print(f"[{index}] cleared proxy env: {', '.join(cleared)}", file=sys.stderr)
    print(f"[{index}] downloading: {url}", file=sys.stderr)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        return {"url": url, "success": False, "error": "yt-dlp not found. Install with: brew install yt-dlp or pip install yt-dlp"}
    except subprocess.TimeoutExpired:
        return {"url": url, "success": False, "error": "download timeout after 300s"}

    created = sorted({p.name for p in output_dir.iterdir()} - before)
    files = [str(output_dir / name) for name in created]
    media_files = [f for f in files if Path(f).suffix.lower() in VIDEO_EXTS or Path(f).suffix.lower() == ".mp3"]
    if result.returncode != 0:
        return {"url": url, "success": False, "platform": platform, "error": (result.stderr or result.stdout).strip()[-1200:], "files": files}
    return {"url": url, "success": bool(media_files), "platform": platform, "media_files": media_files, "files": files}


def main() -> None:
    parser = argparse.ArgumentParser(description="Download viral media with yt-dlp")
    parser.add_argument("--urls", "-u", nargs="+", required=True, help="URLs or share texts")
    parser.add_argument("--output-dir", "-o", default="_temp/viral-inputs")
    parser.add_argument("--cookies-browser", "-c", default="chrome", help="Browser cookie source, empty string to disable")
    parser.add_argument("--audio-only", action="store_true")
    args = parser.parse_args()

    urls = extract_urls(args.urls)
    if not urls:
        print("No valid URL found", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    cookies_browser = args.cookies_browser or None
    results = [run_ytdlp(url, output_dir, idx, cookies_browser, args.audio_only) for idx, url in enumerate(urls, 1)]
    manifest = {"output_dir": str(output_dir), "total": len(results), "success": sum(1 for item in results if item.get("success")), "failed": sum(1 for item in results if not item.get("success")), "results": results}
    (output_dir / "download-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

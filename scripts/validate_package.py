#!/usr/bin/env python3
"""Validate an ecommerce viral remix package has the required delivery structure."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "## 1. 原爆款内容拆解摘要",
    "## 2. 可复用爆款公式",
    "## 3. 自家产品卖点映射表",
    "## 4. 原创宣传脚本",
    "## 5. 短视频分镜表",
    "## 6. 视频生成提示词",
    "## 7. 素材补拍清单",
    "## 8. QA检查表",
]

BRAND_REQUIRED_TERMS = [
    "DEMO BRAND",
    "STOP",
    "PUSH",
    "充电座",
    "二维码",
    "App",
    "自动回充",
    "割前",
    "割后",
    "Let weekends be weekends",
]

SAFETY_TERMS = [
    "不复制",
    "不复用",
    "合规",
    "风险",
]


def find_missing(text: str, terms: list[str]) -> list[str]:
    return [term for term in terms if term not in text]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ecommerce viral remix package output")
    parser.add_argument("package", help="Path to ecommerce-viral-remix-package.md")
    parser.add_argument("--brand-terms", action="store_true", help="Require brand proof-chain terms (see BRAND_REQUIRED_TERMS)")
    parser.add_argument("--require-safety", action="store_true", help="Require safety/compliance terms")
    args = parser.parse_args()

    package_path = Path(args.package).expanduser().resolve()
    if not package_path.exists():
        print(f"FAIL package not found: {package_path}")
        return 2

    text = package_path.read_text(encoding="utf-8", errors="ignore")
    checks: list[tuple[str, list[str]]] = [
        ("required_sections", find_missing(text, REQUIRED_SECTIONS)),
    ]
    if args.brand_terms:
        checks.append(("brand_terms", find_missing(text, BRAND_REQUIRED_TERMS)))
    if args.require_safety:
        checks.append(("safety_terms", find_missing(text, SAFETY_TERMS)))

    failed = False
    for name, missing in checks:
        if missing:
            failed = True
            print(f"FAIL {name}: missing {', '.join(missing)}")
        else:
            print(f"PASS {name}")

    word_count = len(text)
    section_count = sum(1 for section in REQUIRED_SECTIONS if section in text)
    print(f"INFO file={package_path}")
    print(f"INFO chars={word_count} sections={section_count}/{len(REQUIRED_SECTIONS)}")

    if failed:
        return 1
    print("PASS package is structurally complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())

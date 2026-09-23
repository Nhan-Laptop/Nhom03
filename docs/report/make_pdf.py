#!/usr/bin/env python3
"""Xuất README.MD (báo cáo) thành PDF để nộp bài.

Cách làm: README.MD -> HTML (python-markdown) -> PDF (chromium headless --print-to-pdf).
Ảnh minh họa được trỏ bằng đường dẫn tuyệt đối tới docs/evidence/img để chromium đọc được.

Chạy:  python3 docs/report/make_pdf.py
"""

from __future__ import annotations

import html
import pathlib
import re
import shutil
import subprocess
import sys

import markdown

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
OUT_PDF = HERE / "[NT521]-Lab1_24521236-Nhan_24520023-Nhan_24520546-Hoang.pdf"
TMP_HTML = HERE / ".report.build.html"

CSS = """
@page { size: A4; margin: 14mm 13mm; }
* { box-sizing: border-box; }
body { font-family: "DejaVu Sans", sans-serif; font-size: 9.2pt; line-height: 1.45;
       color: #14161f; margin: 0; }
h1 { font-size: 17pt; border-bottom: 2px solid #333; padding-bottom: 6px;
     break-after: avoid; }
h2 { font-size: 13pt; margin-top: 14px; border-bottom: 1px solid #bbb;
     padding-bottom: 3px; break-after: avoid; }
h3 { font-size: 11pt; margin-top: 12px; break-after: avoid; }
h4 { font-size: 10pt; margin-top: 10px; break-after: avoid; }
p, li { orphans: 3; widows: 3; }
code, pre { font-family: "DejaVu Sans Mono", monospace; font-size: 7.6pt; }
code { background: #f2f2f5; padding: 0 2px; border-radius: 2px; }
pre { background: #f7f7fa; border: 1px solid #ddd; border-radius: 3px;
      padding: 6px 8px; overflow: hidden; white-space: pre-wrap;
      break-inside: avoid; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 6px 0; font-size: 8pt;
        break-inside: avoid; }
th, td { border: 1px solid #c8c8d0; padding: 3px 5px; text-align: left;
         vertical-align: top; }
th { background: #eeeef3; }
img { max-width: 100%; border: 1px solid #c8c8d0; border-radius: 3px;
      break-inside: avoid; margin: 4px 0; }
blockquote { border-left: 3px solid #9aa0b5; margin: 6px 0; padding: 2px 10px;
             background: #f7f7fa; }
hr { border: none; border-top: 1px solid #ccc; margin: 12px 0; }
a { color: #0b57d0; text-decoration: none; }
"""


def build_html() -> pathlib.Path:
    md_text = (REPO / "README.MD").read_text(encoding="utf-8")
    body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "sane_lists", "attr_list", "toc"],
    )
    # ảnh dùng đường dẫn tương đối -> đổi sang file:// tuyệt đối để chromium đọc được
    body = re.sub(
        r'src="(?!https?:|file:)([^"]+)"',
        lambda m: f'src="{(REPO / m.group(1)).as_uri()}"',
        body,
    )
    title = html.escape("NT521 – Lab 1 – Báo cáo thực hành nhóm Nhom03")
    doc = (
        "<!doctype html><html lang=\"vi\"><head><meta charset=\"utf-8\">"
        f"<title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>"
    )
    TMP_HTML.write_text(doc, encoding="utf-8")
    return TMP_HTML


def build_pdf(html_path: pathlib.Path) -> None:
    chromium = shutil.which("chromium") or shutil.which("chromium-browser") \
        or shutil.which("google-chrome")
    if not chromium:
        sys.exit("Không tìm thấy chromium/chrome để in PDF.")
    cmd = [
        chromium, "--headless", "--disable-gpu", "--no-sandbox",
        "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=30000",
        f"--print-to-pdf={OUT_PDF}", html_path.as_uri(),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    TMP_HTML.unlink(missing_ok=True)


def main() -> None:
    build_pdf(build_html())
    size_mb = OUT_PDF.stat().st_size / 1_048_576
    print(f"{OUT_PDF.relative_to(REPO)}  ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()

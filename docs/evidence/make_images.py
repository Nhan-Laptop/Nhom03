#!/usr/bin/env python3
"""Sinh ảnh minh họa terminal cho báo cáo Lab 1.

Nguồn dữ liệu: các log thực thi đã lưu trong docs/evidence/ (không gõ lại tay).
Mỗi ảnh có footer ghi rõ file nguồn + khoảng dòng để truy vết.

Chạy:  python3 docs/evidence/make_images.py
"""

from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
OUT = HERE / "img"

# ---------------------------------------------------------------- style ----
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FS, LH, PAD, HEADER, FOOTER = 21, 30, 22, 44, 30

BG = (17, 19, 31)
HEADER_BG = (49, 50, 68)
FOOTER_BG = (30, 30, 46)
BORDER = (88, 91, 112)
FG = (205, 214, 244)
GREEN = (166, 227, 161)
RED = (243, 139, 168)
YELLOW = (249, 226, 175)
CYAN = (137, 220, 235)
PURPLE = (203, 166, 247)
GRAY = (127, 132, 156)

MAXCOLS = 138  # ngắt dòng dài hơn mức này

font = ImageFont.truetype(FONT_REG, FS)
font_b = ImageFont.truetype(FONT_BOLD, FS)
font_hdr = ImageFont.truetype(FONT_BOLD, 17)
font_ftr = ImageFont.truetype(FONT_REG, 15)
CHW = font.getlength("M")


# ------------------------------------------------------------- helpers ----
def _read(path: str) -> list[str]:
    p = REPO / path if not Path(path).is_absolute() else Path(path)
    return p.read_text(encoding="utf-8").split("\n")


CACHE: dict[str, list[str]] = {}


def lines_of(path: str) -> list[str]:
    if path not in CACHE:
        CACHE[path] = _read(path)
    return CACHE[path]


def section(path: str, header_prefix: str, max_lines: int | None = None) -> list[str]:
    """Lấy nội dung của một mục, từ dòng tiêu đề tới tiêu đề kế tiếp cùng/higher cấp."""
    src = lines_of(path)
    start = next(i for i, l in enumerate(src) if l.startswith(header_prefix))
    level = len(header_prefix) - len(header_prefix.lstrip("#"))
    out = [src[start]]
    for line in src[start + 1:]:
        if re.match(r"^#{2,6} ", line):   # chỉ cắt ở tiêu đề mục (##, ###...), bỏ qua '# comment' trong code
            break
        out.append(line)
    while out and not out[-1].strip():
        out.pop()
    if max_lines and len(out) > max_lines:
        out = out[:max_lines] + ["", f"... (xem đầy đủ trong {path})"]
    return out


def span(path: str, first: int, last: int) -> list[str]:
    """Lấy khoảng dòng [first, last] (1-indexed, bao gồm)."""
    src = lines_of(path)
    out = src[first - 1:last]
    while out and not out[-1].strip():
        out.pop()
    return out


def block(text: str) -> list[str]:
    return text.strip("\n").split("\n")


def wrap(lines: list[str], cols: int = MAXCOLS) -> list[str]:
    out: list[str] = []
    for line in lines:
        line = line.replace("\t", "    ")
        if len(line) <= cols:
            out.append(line)
        else:
            out.extend(textwrap.wrap(line, cols, subsequent_indent="    ",
                                     break_long_words=True, drop_whitespace=False))
    return out


def color_of(line: str, diff_patch: bool = False):
    s = line.rstrip()
    if not s.strip():
        return FG
    if re.match(r"^#{2,4} ", s):
        return PURPLE
    up = s.upper()
    if s.startswith("$ "):
        return None  # vẽ 2 màu
    # chỉ coi là lỗi khi 'FAIL/FAILED' đứng riêng (tránh bắt nhầm 'fail-closed')
    if (re.search(r"(?:^|[:\s])FAIL(?:ED)?(?=[\s(:]|$)", up)
            or "CONFLICT" in up or "ERROR" in up or "BLOCKED" in up
            or "DENIED" in up or "UNMERGED" in up or "STILL HAS" in up
            or ("failed" in s and "0 failed" not in s)):
        return RED
    if (up.endswith("OK") or " PASS" in up or "FAST-FORWARD" in up
            or "DELETED BRANCH" in up or "PASS" in up):
        return GREEN
    if diff_patch:   # chỉ tô màu +/− cho ảnh thật sự chứa patch diff
        if s.startswith("+"):
            return GREEN
        if s.startswith("-"):
            return RED
        if s.startswith(("@@", "diff --git", "index ", "--- ", "+++ ")):
            return CYAN
    return FG


#: các ảnh có chứa patch diff -> bật tô màu dòng +/−
DIFF_IMAGES = {"06-b13-diff.png", "20-b21-fix.png"}

def render(title: str, lines: list[str], provenance: str, out_name: str) -> Path:
    body = wrap(lines)
    cols = max((len(l) for l in body), default=40)
    cols = min(max(cols, 46), MAXCOLS + 6)

    w = int(cols * CHW + 2 * PAD)
    h = HEADER + FOOTER + PAD + len(body) * LH + PAD
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)

    # title bar
    d.rectangle([0, 0, w, HEADER], fill=HEADER_BG)
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        d.ellipse([16 + i * 22, HEADER // 2 - 6, 26 + i * 22, HEADER // 2 + 4], fill=c)
    d.text((16 + 3 * 22 + 14, HEADER / 2), title, font=font_hdr, fill=FG, anchor="lm")

    # body
    y = HEADER + PAD
    for line in body:
        col = color_of(line, out_name in DIFF_IMAGES)
        if col is None:                       # dòng lệnh: '$' xanh, phần còn lại trắng
            d.text((PAD, y), "$", font=font_b, fill=GREEN)
            d.text((PAD + 2 * CHW, y), line[2:], font=font, fill=(255, 255, 255))
        else:
            f = font_b if line.startswith(("$", "#")) else font
            d.text((PAD, y), line, font=f, fill=col)
        y += LH

    # provenance footer
    d.rectangle([0, h - FOOTER, w, h], fill=FOOTER_BG)
    d.text((PAD, h - FOOTER / 2), provenance, font=font_ftr, fill=GRAY, anchor="lm")
    d.rectangle([0, 0, w - 1, h - 1], outline=BORDER)

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / out_name
    img.save(path, optimize=True)
    return path


# ------------------------------------------------------------ agent log ----
def agent_activity(path: str, kinds: tuple[str, ...], count: int,
                  max_lines_per: int = 12) -> list[str]:
    """Lấy `count` đoạn suy nghĩ/nội dung đầu tiên của agent từ telemetry JSONL."""
    picked: list[str] = []
    for raw in lines_of(path):
        raw = raw.strip()
        if not raw:
            continue
        try:
            ev = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "background-task-activity" and ev.get("kind") in kinds:
            text = (ev.get("text") or "").strip()
            if text:
                picked.append((ev["kind"], text))
        if len(picked) >= count:
            break
    out: list[str] = []
    for kind, text in picked:
        wrapped = wrap(text.split("\n"), 118)
        if len(wrapped) > max_lines_per:
            wrapped = wrapped[:max_lines_per] + ["    ... (xem telemetry đầy đủ trong file log)"]
        out.append(f"### [{kind}]")
        out.extend(wrapped)
        out.append("")
    return out


# ------------------------------------------------------------- gallery ----
B1 = "docs/evidence/LAB1-B1-evidence.md"
B2 = "docs/evidence/LAB1-B2-evidence.md"
EV1 = "docs/evidence/agent/events.jsonl"
EV2 = "docs/evidence/agent/events-round2.jsonl"

GALLERY = [
    # ---- B.1 ----
    ("01-b11-init.png",
     "B.1.1 — cấu hình Git, git init, trạng thái repository ban đầu",
     span(B1, 12, 16) + [""] + span(B1, 31, 63),
     f"nguồn: {B1} — dòng 12–16 và 31–63"),

    ("02-b12-file.png",
     "B.1.2 — tạo README.MD và kiểm tra tập tin",
     span(B1, 74, 100),
     f"nguồn: {B1} — dòng 74–100"),

    ("03-b12-staging.png",
     "B.1.2 — ba trạng thái: untracked → staged → committed",
     span(B1, 89, 120),
     f"nguồn: {B1} — dòng 89–120"),

    ("04-b12-log.png",
     "B.1.2 — commit đầu tiên và lịch sử commit",
     span(B1, 115, 130),
     f"nguồn: {B1} — dòng 115–130"),

    ("05-b13-change.png",
     "B.1.3 — thêm dòng bằng '>>', kiểm tra và commit",
     span(B1, 133, 160),
     f"nguồn: {B1} — dòng 133–160"),

    ("06-b13-diff.png",
     "B.1.3 — so sánh 2 commit bằng git diff",
     span(B1, 175, 188),
     f"nguồn: {B1} — dòng 175–188"),

    ("07-b14-branch.png",
     "B.1.4 — tạo và chuyển sang nhánh feature",
     span(B1, 192, 208),
     f"nguồn: {B1} — dòng 192–208"),

    ("08-b14-merge.png",
     "B.1.4 — merge feature vào master (Fast-forward) rồi xoá nhánh",
     span(B1, 253, 293),
     f"nguồn: {B1} — dòng 253–293"),

    ("09-b15-sed.png",
     "B.1.5 — sửa cùng một dòng trên 2 nhánh bằng sed",
     span(B1, 302, 344),
     f"nguồn: {B1} — dòng 302–344"),

    ("10-b15-conflict.png",
     "B.1.5 — merge gây xung đột: CONFLICT + unmerged paths",
     span(B1, 345, 372),
     f"nguồn: {B1} — dòng 345–372"),

    ("11-b15-resolve.png",
     "B.1.5 — xoá conflict marker và kiểm tra kết quả",
     span(B1, 373, 397),
     f"nguồn: {B1} — dòng 373–397"),

    ("12-b15-mergecommit.png",
     "B.1.5 — commit kết quả: merge commit có 2 cha",
     span(B1, 398, 428),
     f"nguồn: {B1} — dòng 398–428"),

    ("13-b16-auth.png",
     "B.1.6 — xác thực GitHub bằng gh CLI (Cách A)",
     span(B1, 486, 524),
     f"nguồn: {B1} — dòng 486–524"),

    ("14-b16-push.png",
     "B.1.6 — git remote add origin và git push -u origin master",
     span(B1, 525, 538),
     f"nguồn: {B1} — dòng 525–538"),

    ("15-b16-verify.png",
     "B.1.6 — kiểm tra kết quả trên GitHub",
     span(B1, 539, 574, ),
     f"nguồn: {B1} — dòng 539–574"),

    # ---- B.2 ----
    ("16-b2-baseline.png",
     "B.2 — đưa unittest lên master và tạo 2 nhánh manual/agent",
     span(B2, 27, 69),
     f"nguồn: {B2} — dòng 27–69"),

    ("17-b2-branches.png",
     "B.2 — tạo nhánh manual và agent, trạng thái repository",
     span(B2, 70, 95),
     f"nguồn: {B2} — dòng 70–95"),

    ("18-b21-buggy.png",
     "B.2.1 — bản code trong đề chạy ra kết quả rỗng",
     span(B2, 126, 169),
     f"nguồn: {B2} — dòng 126–169"),

    ("19-b21-fail.png",
     "B.2.1 — unit test: test_search_found FAIL",
     span(B2, 203, 223),
     f"nguồn: {B2} — dòng 203–223"),

    ("20-b21-fix.png",
     "B.2.1 — bản vá lỗi ret_val (Yêu cầu 4)",
     span(B2, 224, 283),
     f"nguồn: {B2} — dòng 224–283"),

    ("21-b21-rbac.png",
     "B.2.1 — RBAC theo policy.py + security test (Yêu cầu 5)",
     section(B2, "### Bước 7. Bổ sung kiểm soát truy cập theo role", max_lines=45),
     f"nguồn: {B2} — mục 'Bước 7'"),

    ("22-b21-11tests.png",
     "B.2.1 — toàn bộ unittest trên nhánh manual: 11 test OK",
     span(B2, 546, 593),
     f"nguồn: {B2} — dòng 546–593"),

    ("23-b22-sandbox.png",
     "B.2.2 — sandbox: chặn commit, chạy agent ở chế độ approval",
     span(B2, 628, 679),
     f"nguồn: {B2} — dòng 628–679"),

    ("24-b22-review.png",
     "B.2.2 — review phát hiện lỗi vi phạm hợp đồng trả về",
     span(B2, 680, 699),
     f"nguồn: {B2} — dòng 680–699"),

    ("25-b22-round2.png",
     "B.2.2 — vòng 2: agent sửa hợp đồng + kiểm chứng 24 test OK",
     span(B2, 700, 745),
     f"nguồn: {B2} — dòng 700–745"),

    # ---- suy nghĩ thật của agent (telemetry) ----
    ("26-agent-think-1.png",
     "Telemetry agent vòng 1 — agent tự lập kế hoạch",
     agent_activity(EV1, ("assistant_text", "reasoning"), 2, max_lines_per=11),
     f"nguồn: {EV1} — trích các sự kiện đầu tiên"),

    ("27-agent-think-2.png",
     "Telemetry agent vòng 2 — agent xử lý feedback của người review",
     agent_activity(EV2, ("reasoning",), 1, max_lines_per=16),
     f"nguồn: {EV2} — trích reasoning của agent ở vòng 2"),
]


def main() -> None:
    for name, title, lines, prov in GALLERY:
        path = render(title, lines, prov, name)
        print(f"{path.relative_to(REPO)}  ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

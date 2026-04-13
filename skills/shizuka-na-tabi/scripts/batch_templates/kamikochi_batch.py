#!/usr/bin/env python3
"""Batch process 上高地 — 秋・黎明・環境音版（無字幕）

素材：Dawn Walk on Kamikochi Nature Trail | Nagano, Japan 4K
URL:  https://www.youtube.com/watch?v=oE9_iDJkNTI
原片：2560×1440 @ 60fps, 1h20m57s, 7.54GB

全片扫描结论（STEP 3.5 密集帧 90s/张）：
- 0-30s 黑屏片头 → 跳过
- 450s (7:30) 建筑物+野餐桌椅（出发点）→ 跳过
- 900s (15:00) 🚫 黑熊目击警告牌（硬编码日文）→ 跳过 14:30-16:00
- 4590s+ (76:30+) 河童橋（人工桥栏/木柱 "L4" 字样）→ 跳过 76:00+

惊喜帧分布：
- 90s (1:30)      梓川+穂高連峰+紅葉+晨光全景 ★★★ Kano #1
- 180s (3:00)     湖面倒影 ★★
- 1440s (24:00)   穂高連峰+湿原草+栈道 ★★★
- 1620s (27:00)   湿原木栈道+穂高 ★★★ Kano #2
- 1710s (28:30)   清澈水池（秘境级）💎
- 2880s (48:00)   秋木板道 ★
- 3420s (57:00)   紅葉道 ★★★ Kano #3
- 3600s (60:00)   杉林紅葉河 ★★
- 3960s (66:00)   苔藓木栈道 ★
"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT, pkg_dir

VIDEO  = str(PROJECT_ROOT / "上高地.mp4")
OUT    = str(PROJECT_ROOT / "上高地_clips")
PKGDIR = str(pkg_dir("上高地"))
os.makedirs(OUT, exist_ok=True)

# ── Clip definitions ─────────────────────────────────────────────────────────
CLIPS = {
    # 精华版：全片最强五帧串烧
    "01_highlight": {
        "title": "秋の上高地 精華版",
        "segments": [
            (90, 150),     # 01:30-02:30  梓川+穂高+紅葉+晨光 ★★★ HOOK Kano#1
            (180, 230),    # 03:00-03:50  湖面倒影
            (1600, 1660),  # 26:40-27:40  湿原木栈道+穂高 ★★★ Kano#2
            (3390, 3450),  # 56:30-57:30  紅葉道 ★★★
            (3570, 3620),  # 59:30-60:20  杉林紅葉河
        ],
        # 60+50+60+60+50 = 280s ≈ 4:40
    },
    # 黎明 · 梓川
    "02_akatsuki": {
        "title": "夜明けの梓川",
        "segments": [
            (60, 150),     # 01:00-02:30  启明+梓川远山 HOOK (90s)
            (180, 240),    # 03:00-04:00  湖面倒影
            (270, 330),    # 04:30-05:30  秋色森林
            (360, 420),    # 06:00-07:00  溪流小径
        ],
        # 90+60+60+60 = 270s ≈ 4:30
    },
    # 湿原 · 穂高連峰
    "03_shitsugen": {
        "title": "湿原と山",
        "segments": [
            (1440, 1500),  # 24:00-25:00  穂高連峰+湿原 ★★★ HOOK
            (1600, 1660),  # 26:40-27:40  木栈道+山
            (1700, 1760),  # 28:20-29:20  清澈水池 💎
            (1260, 1320),  # 21:00-22:00  溪流+森林
        ],
        # 60+60+60+60 = 240s = 4:00
    },
    # 紅葉の道
    "04_koyo": {
        "title": "紅葉の道",
        "segments": [
            (3390, 3470),  # 56:30-57:50  紅葉道 ★★★ HOOK
            (2880, 2940),  # 48:00-49:00  秋木板道
            (3570, 3630),  # 59:30-60:30  杉林紅葉河
            (3780, 3840),  # 63:00-64:00  木栈道溪流秋林
        ],
        # 80+60+60+60 = 260s ≈ 4:20
    },
}

# ── FFmpeg helpers ────────────────────────────────────────────────────────────
def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERR: {r.stderr[-400:]}")
    return r.returncode == 0

def cut_and_merge(segments, merged_path, clip_dir):
    parts = []
    for i, (s, e) in enumerate(segments):
        p = f"{clip_dir}/seg_{i:02d}.mp4"
        # 60fps 原片 → 30fps 输出（抖音不支持 60fps 竖屏全量，且减半带宽）
        # 先 stream copy 剪段，最终 concat 时再统一重编码
        run(f'ffmpeg -y -ss {s} -to {e} -i "{VIDEO}" -c copy "{p}" 2>/dev/null')
        parts.append(p)
    list_path = f"{clip_dir}/list.txt"
    with open(list_path, 'w') as f:
        f.write('\n'.join(f"file '{p}'" for p in parts))
    # 重编码 H.264 + 30fps（抖音推荐）
    run(f'ffmpeg -y -f concat -safe 0 -i "{list_path}" '
        f'-c:v libx264 -crf 18 -preset fast -r 30 '
        f'-c:a aac -b:a 192k "{merged_path}" 2>/dev/null')
    return merged_path

def extract_covers(merged_path, cover_dir):
    os.makedirs(cover_dir, exist_ok=True)
    for t in [3, 15, 30, 60, 90, 120]:
        run(f'ffmpeg -y -ss {t} -i "{merged_path}" -vframes 1 '
            f'"{cover_dir}/frame_{t:03d}s.png" 2>/dev/null')
    print(f"  封面帧已提取 → {cover_dir}")

# ── Main ─────────────────────────────────────────────────────────────────────
for key, cfg in CLIPS.items():
    title    = cfg["title"]
    segments = cfg["segments"]
    clip_dir = f"{OUT}/{key}"
    os.makedirs(clip_dir, exist_ok=True)

    merged = f"{clip_dir}/merged.mp4"
    final  = f"{PKGDIR}/{key}_final.mp4"

    total = sum(e - s for s, e in segments)
    print(f"\n▶ [{key}] {title}  ({len(segments)}段, ~{total//60}分{total%60}秒)")

    print("  剪辑合并...")
    cut_and_merge(segments, merged, clip_dir)

    # 直接用 merged 作为 final（環境音版，無字幕）
    run(f'cp "{merged}" "{final}"')

    cover_dir = f"{clip_dir}/封面"
    extract_covers(merged, cover_dir)

    size = os.path.getsize(final) / 1024 / 1024 if os.path.exists(final) else 0
    print(f"  ✓ → {final} ({size:.0f}MB)")

print("\n🎉 全部完成！取件路径：")
print(f"  {PKGDIR}/")
for key in CLIPS:
    p = f"{PKGDIR}/{key}_final.mp4"
    if os.path.exists(p):
        size = os.path.getsize(p) / 1024 / 1024
        print(f"    {key}_final.mp4  ({size:.0f}MB)")

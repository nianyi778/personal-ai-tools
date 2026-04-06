#!/usr/bin/env python3
"""Batch process 馬籠宿→妻籠宿 — 環境音版（无字幕，夏の夕暮れ・中山道）"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT

VIDEO  = str(PROJECT_ROOT / "magome.mp4")
OUT    = str(PROJECT_ROOT / "magome_clips")
PKGDIR = str(PROJECT_ROOT / "📦発布包" / "馬籠")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PKGDIR, exist_ok=True)

# ── 全片扫描结论 ───────────────────────────────────────────────
# 素材：馬籠宿→妻籠宿（1h03m，環境音のみ）
# 水印："ambcnt" 从约 2200s 开始出现 → 所有片段必须在 2100s 以前
# 概念：中山道を歩いた、夏の夕暮れ（石畳×田園×粉紫夕空）
# 分区：
#   宿場エリア  (130-460s):  妻籠宿・馬籠宿の石畳，誰もいない
#   田園エリア  (1340-1850s): 田園路・夕景・水田×粉紫夕空
#
# Kano 惊喜帧：1718s 水田×粉紫夕空（全片最强画面）
# HOOK 铁律：石畳漫步（最低跳出率素材类型）
#
# 01_highlight  夏の夕暮れ  ~3:50  (40+50+80+60=230s)
# 02_machinaka  誰もいない石畳  ~4:20  (60+65+75+60=260s)
# 03_tasogare   夕暮れの中山道  ~4:30  (40+80+70+80=270s)

CLIPS = {
    "01_highlight": {
        "title": "夏の夕暮れ、中山道を歩いた",
        "segments": [
            (230,  270),  # 03:50-04:30  妻籠宿 石畳・無人  HOOK
            (1700, 1750), # 28:20-29:10  水田×粉紫夕空  Kano惊喜帧（merged第40s）
            (1340, 1420), # 22:20-23:40  田園路・黄昏前
            (340,  400),  # 05:40-06:40  馬籠宿 石畳・建物並ぶ
        ],
    },
    "02_machinaka": {
        "title": "誰もいない石畳の宿場",
        "segments": [
            (210,  270),  # 03:30-04:30  妻籠宿 石畳  HOOK
            (130,  195),  # 02:10-03:15  宿場入口・分岐
            (300,  375),  # 05:00-06:15  石畳中段・花咲く宿場
            (400,  460),  # 06:40-07:40  石畳後段・建物
        ],
    },
    "03_tasogare": {
        "title": "夕暮れの中山道",
        "segments": [
            (1430, 1470), # 23:50-24:30  石壁路  HOOK
            (1670, 1750), # 27:50-29:10  水田×粉紫夕空  Kano惊喜帧（merged第40s）
            (1340, 1410), # 22:20-23:30  田園路
            (1750, 1830), # 29:10-30:30  夕暮れ後の静寂
        ],
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
        run(f'ffmpeg -y -ss {s} -to {e} -i "{VIDEO}" -c copy "{p}" 2>/dev/null')
        parts.append(p)
    list_path = f"{clip_dir}/list.txt"
    with open(list_path, 'w') as f:
        f.write('\n'.join(f"file '{p}'" for p in parts))
    run(f'ffmpeg -y -f concat -safe 0 -i "{list_path}" '
        f'-c:v libx264 -crf 18 -preset fast -c:a aac -b:a 128k "{merged_path}" 2>/dev/null')
    return merged_path

def extract_covers(merged_path, cover_dir):
    os.makedirs(cover_dir, exist_ok=True)
    for t in [3, 15, 30, 60, 90, 120, 150, 180]:
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

    # 環境音版：merged = final（無字幕）
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

#!/usr/bin/env python3
"""Batch process 小樽 — 環境音版（无字幕，冬の雪）"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT

VIDEO  = str(PROJECT_ROOT / "小樽.mp4")
OUT    = str(PROJECT_ROOT / "小樽_clips")
PKGDIR = str(PROJECT_ROOT / "📦発布包" / "小樽")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PKGDIR, exist_ok=True)

# ── 全片扫描结论 ───────────────────────────────────────────────
# 素材：小樽 冬の街歩き（22:34，1080p，環境音のみ）
# 频道：Sounds of Otaru — 无解说，纯环境音
# 画面：雪景街道 → 運河 → 倉庫群 → 夕暮れ
# 无水印、无人物、无字幕
#
# 01_highlight  精华  ~4:00
#   HOOK: 10-70    冬の石畳路地・雪  HOOK（雪景+街道）60s
#         80-140   運河沿いの倉庫群                        60s
#         240-300  雪降る街角・ガス灯                       60s
#         520-580  夕暮れの運河・静けさ                     60s
#   total: 240s = 4:00 ✓

CLIPS = {
    "01_highlight": {
        "title": "小樽 冬の街歩き",
        "segments": [
            (10,   70),   # 00:10-01:10  冬の石畳路地・雪  HOOK
            (80,   140),  # 01:20-02:20  運河沿いの倉庫群
            (240,  300),  # 04:00-05:00  雪降る街角・ガス灯
            (520,  580),  # 08:40-09:40  夕暮れの運河・静けさ
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

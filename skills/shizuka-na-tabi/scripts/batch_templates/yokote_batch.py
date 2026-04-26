#!/usr/bin/env python3
"""Batch process 横手城 — 環境音版（无字幕，冬の雪・城・神社）"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT

VIDEO  = str(PROJECT_ROOT / "横手城.mp4")
OUT    = str(PROJECT_ROOT / "横手城_clips")
PKGDIR = str(PROJECT_ROOT / "📦発布包" / "横手城")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PKGDIR, exist_ok=True)

# ── 全片扫描结论 ───────────────────────────────────────────────
# 素材：横手城 雪の夕暮れ（59:50，4K 60fps，環境音のみ）
# 频道：Rambalac — no talking, natural surround sound only
# 水印：无
# 人物：极少，可跳过
# 分区：
#   駅前エリア (0-600s): 雪の商店街・街灯
#   神社エリア (600-1800s): 小神社・鳥居・石段
#   城エリア (1800-3500s): 横手城・天守閣・城壁
#   城下町 (3500-4800s): 路地裏・夕暮れ
#   夜エリア (4800-3590s): 街灯・雪夜
#
# 01_highlight  雪の城下町  ~4:00
#   HOOK: 180-240  横手城・雪の天守閣  HOOK（城+雪）60s
#         720-780  神社・鳥居・雪                            60s
#         1500-1570 城壁・雪の石段                           70s
#         2400-2470 夕暮れの城下町                          70s
#   total: 260s ≈ 4:20 ✓
#
# 02_jinja  雪の神社  ~4:00
#   HOOK: 600-660  鳥居の朱色・雪  HOOK                    60s
#         900-960  境内・雪の参道                            60s
#         1200-1260 手水舎・雪                               60s
#         2100-2160 雪降る境内                              60s
#   total: 240s = 4:00 ✓
#
# 03_castle  横手城  ~4:00
#   HOOK: 1800-1860 天守閣正面・雪  HOOK                    60s
#         2100-2160 城内・雪の庭園                          60s
#         2400-2460 城壁からの眺望                          60s
#         2700-2760 雪の大手門                              60s
#   total: 240s = 4:00 ✓
#
# 04_yoru  雪夜の街灯  ~3:30
#   HOOK: 3000-3060 路地裏の灯・雪  HOOK                   60s
#         3200-3250 街灯と雪                               50s
#         3400-3450 夜の駅前                               50s
#   total: 160s ≈ 2:40 ✓ (偏短，可与03合并)

CLIPS = {
    "01_highlight": {
        "title": "雪の城下町",
        "segments": [
            (180,  240),  # 03:00-04:00  横手城・雪の天守閣  HOOK
            (720,  780),  # 12:00-13:00  神社・鳥居・雪
            (1500, 1570), # 25:00-26:10  城壁・雪の石段
            (2400, 2470), # 40:00-41:10  夕暮れの城下町
        ],
    },
    "02_jinja": {
        "title": "雪の神社",
        "segments": [
            (600,  660),  # 10:00-11:00  鳥居の朱色・雪  HOOK
            (900,  960),  # 15:00-16:00  境内・雪の参道
            (1200, 1260), # 20:00-21:00  手水舎・雪
            (2100, 2160), # 35:00-36:00  雪降る境内
        ],
    },
    "03_castle": {
        "title": "横手城",
        "segments": [
            (1800, 1860), # 30:00-31:00  天守閣正面・雪  HOOK
            (2100, 2160), # 35:00-36:00  城内・雪の庭園
            (2400, 2460), # 40:00-41:00  城壁からの眺望
            (2700, 2760), # 45:00-46:00  雪の大手門
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

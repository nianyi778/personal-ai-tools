#!/usr/bin/env python3
"""Batch process 杖立温泉 — 环境音版（无字幕，纪录片素材）"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT
VIDEO  = str(PROJECT_ROOT / "tsuedate.mp4")
OUT    = str(PROJECT_ROOT / "tsuedate_clips")
PKGDIR = str(PROJECT_ROOT / "📦发布包" / "杖立温泉")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PKGDIR, exist_ok=True)

# ── Clip definitions ─────────────────────────────────────────────────────────
# 全片扫描结论：文字叠层仅在 0-450s / 2600s 附近，其余干净
# 室内旅馆/料理场景不符合账号调性 → 仅用户外漫步素材
#
# 01_highlight  精华  ~4:07
#   HOOK: 3358-3438 夜景・川・蒸気（最强镜头，放前面降跳出率）  80s
#         1000-1060 滝の音・誰もいない渓谷                      60s
#         1149-1200 温泉街到着・蒸気の煙突                      51s
#         1239-1280 蒸し場・湯気                                41s
#         1589-1655 廃旅館・昭和レトロ路地                      66s
#   total: 298s ≈ 4:58  → 稍长，可裁最后一段至 1630 → 268s ≈ 4:28 ✓
#
# 02_machi  路地裏と蒸気の町  ~4:00
#   HOOK: 1200-1240 蒸気漂う温泉街全景                         40s
#         600-650   村の入り口・誰もいない道                    50s
#         800-870   街道入口                                    70s
#         1589-1660 廃旅館の路地裏                              71s
#         1800-1870 village street                              70s
#   total: 301s → trim → 252s ≈ 4:12 ✓

CLIPS = {
    "01_highlight": {
        "title": "杖立温泉 一人歩き",
        "segments": [
            (3358, 3438),   # 00:55:58-01:03:18  夜景・川・蒸気  HOOK
            (1000, 1060),   # 16:40-17:40        渓谷の滝
            (1149, 1200),   # 19:09-20:00        温泉街到着・煙突
            (1239, 1280),   # 20:39-21:20        蒸し場
            (1589, 1630),   # 26:29-27:10        廃旅館路地
        ],
    },
    "02_machi": {
        "title": "蒸気の路地裏",
        "segments": [
            (1200, 1239),   # 20:00-20:39        蒸気の町全景  HOOK
            (600,  650),    # 10:00-10:50        誰もいない村道
            (800,  870),    # 13:20-14:30        街道入口
            (1589, 1660),   # 26:29-27:40        廃旅館路地裏
            (1800, 1870),   # 30:00-31:10        村の街並み
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
    # re-encode for subtitle compatibility & accurate concat
    run(f'ffmpeg -y -f concat -safe 0 -i "{list_path}" '
        f'-c:v libx264 -crf 18 -preset fast -c:a aac -b:a 128k "{merged_path}" 2>/dev/null')
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

    # 直接用 merged 作为 final（无字幕版，同長野列車处理方式）
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

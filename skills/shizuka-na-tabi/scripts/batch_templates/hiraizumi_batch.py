#!/usr/bin/env python3
"""Batch process 平泉 — 環境音版（无字幕，秋の紅葉・毛越寺・中尊寺）"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT

VIDEO  = str(PROJECT_ROOT / "hiraizumi.mp4")
OUT    = str(PROJECT_ROOT / "hiraizumi_clips")
PKGDIR = str(PROJECT_ROOT / "📦発布包" / "平泉")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PKGDIR, exist_ok=True)

# ── 全片扫描结论 ───────────────────────────────────────────────
# 素材：平泉 Rambalac 1080p60（1h18m，環境音，無水印）
# 频道：Rambalac ✅（无水印，可信赖）
# 概念：岩手・平泉 秋の紅葉巡礼（UNESCO世界遺産）
# 精华区：
#   Zone A (1650-2600s): 毛越寺庭園 — 石垣+紅葉+池+大松
#   Zone B (2960-3010s): 橙红枫树特写（全片最强HOOK）
# 避开：
#   0-1600s: 住宅街・普通道路
#   2850s+:  町中・駐車場（一部猫コーナー3390-3460除外）
#
# Kano 惊喜帧：2129s 毛越寺池+大松+紅葉（全片最美庭园）
#
# 01_highlight  精华  ~4:20  (50+70+70+70=260s)
#   HOOK: 2960-3010  橙红枫树 HOOK（蓝天×全帧橙色）
#   Kano: 2090-2160  毛越寺池+大松+紅葉（merged第50s）✓
#         1690-1760  石垣+紅葉入口
#         2470-2540  庭园水草+落ち葉
#
# 02_teien  毛越寺庭園  ~4:30  (60+70+70+70=270s)
#   HOOK: 1690-1750  石垣+紅葉 HOOK
#   Kano: 2090-2160  松+池+紅葉（merged第60s）✓
#         2340-2410  広い芝生+松林
#         2460-2530  庭园池縁
#
# 03_koyo  紅葉の道  ~4:15  (55+50+80+70=255s)
#   HOOK: 2040-2095  紅葉のトンネル HOOK
#   Kano: 2960-3010  橙色枫树（merged第55s）✓
#         2680-2760  中尊寺+黄葉
#         3390-3460  猫+民家（意外结尾）

CLIPS = {
    "01_highlight": {
        "title": "平泉の秋、紅葉を歩いた",
        "segments": [
            (2960, 3010), # 49:20-50:10  橙红枫树 HOOK
            (2090, 2160), # 34:50-36:00  毛越寺池+大松+紅葉  Kano惊喜帧
            (1690, 1760), # 28:10-29:20  石垣+紅葉入口
            (2470, 2540), # 41:10-42:20  庭园水草+落ち葉
        ],
    },
    "02_teien": {
        "title": "毛越寺、静かな庭に紅葉が落ちていた",
        "segments": [
            (1690, 1750), # 28:10-29:10  石垣+紅葉 HOOK
            (2090, 2160), # 34:50-36:00  松+池+紅葉  Kano惊喜帧
            (2340, 2410), # 39:00-40:10  広い芝生+松林
            (2460, 2530), # 41:00-42:10  庭园池縁
        ],
    },
    "03_koyo": {
        "title": "紅葉の下を、ただ歩いた",
        "segments": [
            (2040, 2095), # 34:00-34:55  紅葉のトンネル HOOK
            (2960, 3010), # 49:20-50:10  橙色枫树  Kano惊喜帧
            (2680, 2760), # 44:40-46:00  中尊寺+黄葉
            (3390, 3460), # 56:30-57:40  猫+民家（秘密のエンディング）
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
    for t in [3, 15, 30, 60, 90, 120, 150, 180, 210]:
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

#!/usr/bin/env python3
"""Batch process 有馬温泉 — 環境音版（无字幕，温泉街・蒸汽）"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT

VIDEO  = "/tmp/style_check_arima.mp4"  # 使用已下载的样本
OUT    = str(PROJECT_ROOT / "有馬温泉_clips")
PKGDIR = str(PROJECT_ROOT / "📦発布包" / "有馬温泉")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PKGDIR, exist_ok=True)

# ── 全片扫描结论 ───────────────────────────────────────────────
# 素材：有馬温泉 Walking Tour（37:20，1080p 60fps HDR，環境音のみ）
# 频道：Video Street View Japan — no talking, binaural audio
# 水印：无
# 人物：极少
# 分区：
#   入り口エリア (0-300s): 温泉街入口・町並み
#   街並みエリア (300-900s): 温泉街中心・蒸汽・古い建物
#   山道エリア (900-1500s): 山道・緑・静かな道
#   奥地エリア (1500-2239s): 温泉街奥・建物・階段
#
# 01_highlight  有馬温泉・精華  ~4:00
#   HOOK: 180-240  温泉街・蒸汽  HOOK（蒸汽+建筑）60s
#         300-360  古い建物・温泉雰囲気                    60s
#         600-660  山道・緑・静けさ                      60s
#         1200-1260 温泉街・夕暮れ感                      60s
#   total: 240s = 4:00 ✓
#
# 02_steam  有馬温泉・山道と蒸汽  ~4:00
#   HOOK: 900-960  山道・緑  HOOK                        60s
#         1000-1060 山道・静けさ                         60s
#         1600-1660 温泉街奥・蒸汽                       60s
#         1800-1860 建物・階段                           60s
#   total: 240s = 4:00 ✓

CLIPS = {
    "01_highlight": {
        "title": "有馬温泉",
        "segments": [
            (180,  240),  # 03:00-04:00  温泉街・蒸汽  HOOK
            (300,  360),  # 05:00-06:00  古い建物・温泉雰囲気
            (600,  660),  # 10:00-11:00  山道・緑・静けさ
            (1200, 1260), # 20:00-21:00  温泉街・夕暮れ感
        ],
    },
    "02_steam": {
        "title": "有馬温泉・奥の道",
        "segments": [
            (900,  960),  # 15:00-16:00  山道・緑  HOOK
            (1000, 1060), # 16:40-17:40  山道・静けさ
            (1600, 1660), # 26:40-27:40  温泉街奥・蒸汽
            (1800, 1860), # 30:00-31:00  建物・階段
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

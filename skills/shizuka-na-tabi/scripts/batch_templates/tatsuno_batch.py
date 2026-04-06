#!/usr/bin/env python3
"""Batch process 龍野城下町 — 環境音版（无字幕，春の桜・雨）"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT

VIDEO  = str(PROJECT_ROOT / "tatsuno.mp4")
OUT    = str(PROJECT_ROOT / "tatsuno_clips")
PKGDIR = str(PROJECT_ROOT / "📦発布包" / "龍野")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PKGDIR, exist_ok=True)

# ── 全片扫描结论 ───────────────────────────────────────────────
# 素材：龍野城下町 + 春の桜（1h01m，環境音のみ）
# 水印：1100-1300s 附近河川段有 "ampient" 水印 → 全部跳过
# 人物：1800s 附近有行人 → 跳过
# 分区：
#   城下町エリア (0-1800s): 夜明け前の石畳路地，最低跳出率素材
#   桜エリア    (2100-3600s): 寺院・城山・神社，最高涨粉素材
#
# 01_highlight  精华  ~4:10
#   HOOK: 25-85   しだれ桜・石畳・雨滴  HOOK（水面+花+誰もいない）60s
#         300-360  城下町の路地・夜明け                            60s
#         2100-2170 寺院境内・桜・赤幟                             70s
#         3300-3360 神社・桜・黄金光                               60s
#   total: 250s ≈ 4:10 ✓
#
# 02_sakura  桜と雨の龍野  ~4:10
#   HOOK: 25-85   しだれ桜の雨  HOOK                              60s
#         2100-2190 寺院の桜・幟                                   90s → trim
#         2700-2750 桜の丘から城下を望む                           50s
#         3500-3570 神社・桜・黎明光                               70s
#   total: 250s ≈ 4:10 ✓
#
# 03_machinaka  誰もいない城下町  ~4:00
#   HOOK: 60-140   城下町の石畳・夜明け  HOOK                      80s
#         300-370  城下町の路地続き                                 70s
#         1500-1570 城下町後半                                      70s
#         2700-2740 城山からの桜（締め）                            40s
#   total: 260s ≈ 4:20 ✓

CLIPS = {
    "01_highlight": {
        "title": "龍野 春の夜明け",
        "segments": [
            (25,   85),   # 00:25-01:25  しだれ桜・石畳・雨滴  HOOK
            (300,  360),  # 05:00-06:00  城下町の路地・夜明け
            (2100, 2170), # 35:00-36:10  寺院境内・桜・赤幟
            (3300, 3360), # 55:00-56:00  神社・桜・黄金光
        ],
    },
    "02_sakura": {
        "title": "桜と雨の龍野",
        "segments": [
            (25,   85),   # 00:25-01:25  しだれ桜の雨  HOOK
            (2100, 2170), # 35:00-36:10  寺院の桜・幟
            (2700, 2750), # 45:00-45:50  桜の丘から城下を望む
            (3500, 3580), # 58:20-59:40  神社・桜・黎明光
        ],
    },
    "03_machinaka": {
        "title": "誰もいない城下町",
        "segments": [
            (60,   140),  # 01:00-02:20  城下町の石畳・夜明け  HOOK
            (300,  370),  # 05:00-06:10  城下町の路地続き
            (1500, 1570), # 25:00-26:10  城下町後半
            (2700, 2740), # 45:00-45:40  城山からの桜（締め）
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

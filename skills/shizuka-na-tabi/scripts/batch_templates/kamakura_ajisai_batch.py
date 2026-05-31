#!/usr/bin/env python3
"""镰仓紫陽花（Scenery of Japan vLa6VUnMnJ0）— 3 条环境音版
路线：明月院（前30min）→ 長谷寺（96-118min）
截断：7100s 之前（片尾 Scenery of Japan LOGO 在 ~7200s）
"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT

VIDEO  = str(PROJECT_ROOT / "镰仓紫陽花.mkv")
OUT    = str(PROJECT_ROOT / "镰仓紫陽花_clips")
PKGDIR = str(PROJECT_ROOT / "📦発布包" / "镰仓紫陽花")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PKGDIR, exist_ok=True)

CLIPS = {
    "01_highlight": {
        "title": "雨の鎌倉・紫陽花精華",
        "segments": [
            (600, 660),    # 10:00-11:00 明月院・蓝紫陽花隧道 HOOK
            (900, 960),    # 15:00-16:00 明月院内部
            (6420, 6480),  # 107:00-108:00 長谷寺・紫陽花+雨衣背影
            (6600, 6660),  # 110:00-111:00 長谷寺段
        ],
    },
    "02_meigetsu": {
        "title": "明月院・雨の紫陽花道",
        "segments": [
            (300, 360),    # 5:00-6:00   明月院入口
            (600, 660),    # 10:00-11:00 紫陽花隧道（HOOK）
            (1200, 1260),  # 20:00-21:00 明月院中段
            (1500, 1560),  # 25:00-26:00 明月院後段
        ],
    },
    "03_hasedra": {
        "title": "長谷寺・紫陽花と雨",
        "segments": [
            (5760, 5820),  # 96:00-97:00 長谷周辺・历史街道 HOOK
            (6300, 6360),  # 105:00-106:00 長谷寺接近
            (6420, 6480),  # 107:00-108:00 長谷寺・紫陽花群
            (6900, 6960),  # 115:00-116:00 長谷寺後段（截断前）
        ],
    },
}


def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERR: {r.stderr[-300:]}")
    return r.returncode == 0


def cut_and_merge(segments, merged_path, clip_dir):
    parts = []
    for i, (s, e) in enumerate(segments):
        p = f"{clip_dir}/seg_{i:02d}.mkv"
        run(f'ffmpeg -y -ss {s} -to {e} -i "{VIDEO}" -c copy "{p}" 2>/dev/null')
        parts.append(p)
    list_path = f"{clip_dir}/list.txt"
    with open(list_path, 'w') as f:
        f.write('\n'.join(f"file '{p}'" for p in parts))
    run(f'ffmpeg -y -f concat -safe 0 -i "{list_path}" '
        f'-vf "scale=1920:1080:flags=lanczos" '
        f'-c:v h264_videotoolbox -b:v 8M -maxrate 12M -bufsize 16M '
        f'-c:a aac -b:a 128k -movflags +faststart "{merged_path}" 2>/dev/null')
    return merged_path


def extract_covers(merged_path, cover_dir):
    os.makedirs(cover_dir, exist_ok=True)
    for t in [3, 15, 30, 60, 90, 120, 150, 180]:
        run(f'ffmpeg -y -ss {t} -i "{merged_path}" -vframes 1 '
            f'"{cover_dir}/frame_{t:03d}s.png" 2>/dev/null')


if __name__ == "__main__":
    for key, cfg in CLIPS.items():
        clip_dir = f"{OUT}/{key}"
        os.makedirs(clip_dir, exist_ok=True)
        merged = f"{clip_dir}/merged.mp4"
        final  = f"{PKGDIR}/{key}_final.mp4"

        total = sum(e - s for s, e in cfg["segments"])
        print(f"\n▶ [{key}] {cfg['title']} ({total}s)")

        cut_and_merge(cfg["segments"], merged, clip_dir)
        run(f'cp "{merged}" "{final}"')
        extract_covers(merged, f"{clip_dir}/封面")

        size = os.path.getsize(final) / 1024 / 1024 if os.path.exists(final) else 0
        print(f"  ✓ {final} ({size:.0f}MB)")

    print("\n✅ 完成！取件路径：")
    print(f"  {PKGDIR}/")

#!/usr/bin/env python3
"""4 素材批处理 — 草津 / 熊野 / 尾道 / 角館（环境音版，直接重压 1080p 8Mbps）"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT

CONFIGS = {
    "草津温泉": {
        "video": str(PROJECT_ROOT / "草津温泉.mp4"),
        "ext": "mp4",
        "clips": {
            "01_highlight": {
                "title": "雪の湯畑・草津精華",
                "segments": [
                    (1620, 1680),  # 27:00-28:00  夜湯畑全景+蒸气（Hook）
                    (540, 600),    # 09:00-10:00  巨大圣诞树夜灯
                    (1080, 1140),  # 18:00-19:00  夜雪小巷+店面
                    (1500, 1560),  # 25:00-26:00  夜街灯笼小巷
                ],
            },
            "02_yoru": {
                "title": "草津、夜の散歩",
                "segments": [
                    (120, 180),    # 02:00-03:00  傍晚街口（避 Google Earth 0-60s）
                    (1260, 1320),  # 21:00-22:00  夜雪街道+车
                    (1140, 1200),  # 19:00-20:00  夜雪巷
                    (1560, 1620),  # 26:00-27:00  夜街道
                ],
            },
        },
    },
    "熊野古道": {
        "video": str(PROJECT_ROOT / "熊野古道.mp4"),
        "ext": "mp4",
        "clips": {
            "01_highlight": {
                "title": "熊野古道精華",
                "segments": [
                    (300, 360),    # 5:00-6:00   苔阶+竹林（Hook）
                    (1200, 1260),  # 20:00-21:00 古道杉树
                    (1800, 1860),  # 30:00-31:00 那智大社接近
                    (2700, 2760),  # 45:00-46:00 那智瀑布
                ],
            },
            "02_kodo": {
                "title": "古道、雨の中を歩く",
                "segments": [
                    (600, 660),    # 10:00-11:00 古道入り口
                    (1080, 1140),  # 18:00-19:00 杉並木
                    (1500, 1560),  # 25:00-26:00 古道中段
                    (1680, 1740),  # 28:00-29:00 大社接近
                ],
            },
            "03_taki": {
                "title": "那智の滝",
                "segments": [
                    (1980, 2040),  # 33:00-34:00 大社境内
                    (2400, 2460),  # 40:00-41:00 滝に向かう
                    (2820, 2880),  # 47:00-48:00 滝の前
                    (3000, 3060),  # 50:00-51:00 滝の音
                ],
            },
        },
    },
    "尾道": {
        "video": str(PROJECT_ROOT / "尾道.mkv"),
        "ext": "mkv",
        "clips": {
            "01_highlight": {
                "title": "尾道精華",
                "segments": [
                    (900, 960),    # 15:00-16:00 商店街拱顶
                    (1500, 1560),  # 25:00-26:00 千光寺坂道
                    (1800, 1860),  # 30:00-31:00 山陰小路
                    (2400, 2460),  # 40:00-41:00 下山港景
                ],
            },
            "02_senkoji": {
                "title": "千光寺の坂道",
                "segments": [
                    (1320, 1380),  # 22:00-23:00 山坡
                    (1500, 1560),  # 25:00-26:00 千光寺
                    (1620, 1680),  # 27:00-28:00 寺境内
                    (1740, 1800),  # 29:00-30:00 山陰小路入り
                ],
            },
            "03_machi": {
                "title": "尾道の街と海",
                "segments": [
                    (900, 960),    # 15:00-16:00 商店街
                    (1080, 1140),  # 18:00-19:00 商店街内
                    (2100, 2160),  # 35:00-36:00 下山街
                    (2400, 2460),  # 40:00-41:00 港景
                ],
            },
        },
    },
    "角館": {
        "video": str(PROJECT_ROOT / "角館.mkv"),
        "ext": "mkv",
        "clips": {
            "01_highlight": {
                "title": "雪夜の武家屋敷",
                "segments": [
                    (300, 360),    # 5:00-6:00   夜雪入口
                    (900, 960),    # 15:00-16:00 武家屋敷主街
                    (1500, 1560),  # 25:00-26:00 黒板塀+雪
                    (2100, 2160),  # 35:00-36:00 静かな路
                ],
            },
            "02_yakata": {
                "title": "黒板塀と雪",
                "segments": [
                    (600, 660),    # 10:00-11:00 武家屋敷正面
                    (1200, 1260),  # 20:00-21:00 路灯+雪堆
                    (1800, 1860),  # 30:00-31:00 街灯下の屋敷
                    (2400, 2460),  # 40:00-41:00 夜路尽头
                ],
            },
            "03_yuki": {
                "title": "雪、ただ降りていた",
                "segments": [
                    (180, 240),    # 3:00-4:00   雪夜入口
                    (1080, 1140),  # 18:00-19:00 静街
                    (1620, 1680),  # 27:00-28:00 街角
                    (2280, 2340),  # 38:00-39:00 终段
                ],
            },
        },
    },
}


def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERR: {r.stderr[-400:]}")
    return r.returncode == 0


def cut_and_merge(video, segments, merged_path, clip_dir, ext):
    """Stream copy 切片 → concat + 重压到 1080p H.264 8Mbps（h264_videotoolbox 硬件加速）"""
    parts = []
    for i, (s, e) in enumerate(segments):
        p = f"{clip_dir}/seg_{i:02d}.{ext}"
        # stream copy 切片（秒级），用 -ss 在 -i 后保证准确切割
        run(f'ffmpeg -y -ss {s} -to {e} -i "{video}" -c copy "{p}" 2>/dev/null')
        parts.append(p)
    list_path = f"{clip_dir}/list.txt"
    with open(list_path, 'w') as f:
        f.write('\n'.join(f"file '{p}'" for p in parts))
    # concat + 1080p 重压（硬件加速）
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


def process_location(name, cfg):
    video = cfg["video"]
    ext = cfg["ext"]
    out = str(PROJECT_ROOT / f"{name}_clips")
    pkgdir = str(PROJECT_ROOT / "📦発布包" / name)
    os.makedirs(out, exist_ok=True)
    os.makedirs(pkgdir, exist_ok=True)

    print(f"\n━━━━━ {name} ━━━━━")
    for key, clipcfg in cfg["clips"].items():
        title = clipcfg["title"]
        segments = clipcfg["segments"]
        clip_dir = f"{out}/{key}"
        os.makedirs(clip_dir, exist_ok=True)

        merged = f"{clip_dir}/merged.mp4"
        final = f"{pkgdir}/{key}_final.mp4"

        total = sum(e - s for s, e in segments)
        print(f"▶ [{name}/{key}] {title} ({len(segments)}段, {total}秒)")

        cut_and_merge(video, segments, merged, clip_dir, ext)

        # 環境音版：merged = final（无字幕）
        run(f'cp "{merged}" "{final}"')

        cover_dir = f"{clip_dir}/封面"
        extract_covers(merged, cover_dir)

        size = os.path.getsize(final) / 1024 / 1024 if os.path.exists(final) else 0
        print(f"  ✓ → {final} ({size:.0f}MB)")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", help="只处理指定素材（不传则处理全部）")
    args = parser.parse_args()

    targets = args.only or list(CONFIGS.keys())
    for name in targets:
        if name not in CONFIGS:
            print(f"⚠️ 跳过未知素材: {name}")
            continue
        process_location(name, CONFIGS[name])

    print("\n🎉 全部完成！")

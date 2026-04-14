#!/usr/bin/env python3
"""Batch process 江之岛 — 大雨早朝・環境音版（無字幕・竖屏直出）

素材：Heavy rain Enoshima early morning walk, Japan [4K HDR]
URL:  https://www.youtube.com/watch?v=848EpwPmQfA
原片：2560×1440 @ 59fps, 2h18m, 13.2GB, nadawalk

全片扫描結論（120s/帧 × 70 帧）：
- 120s (2:00)   参道商店街+雨+無人 ✓（有日文店名但早朝氛围好）
- 360s (6:00)   💎 江島神社+大雨+石面反光 ★★★ Kano#2
- 720s (12:00)  ⚠️ 浮世絵看板 → 跳过 700-780
- 1200s (20:00) ⚠️「山ふたつ」看板 → 跳过 1150-1260
- 1800s (30:00) 🔥 雨中森林小径
- 2400s (40:00) 💎💎 海岸岩石+大浪+雨雾 ★★★ Kano#1
- 3000s (50:00) 巷弄+石阶（回程）
- 3600s (60:00) 窄巷+石阶
- 4200s (70:00) 🔥 苔藓壁+雨水
- 4800s (80:00) 🔥 赤い小屋+石阶+緑
- 5400s (90:00) 海岸線道路
- 6000s (100:00) ⚠️ 商業招牌 → 跳过 5900-6120
- 6600s (110:00) 江之電沿線 ✓
- 7200s (120:00) 住宅街（一般）
- 7800s (130:00) ⚠️ 招牌 → 跳过 7700-7900
"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT, pkg_dir

VIDEO  = str(PROJECT_ROOT / "江之岛.mp4")
OUT    = str(PROJECT_ROOT / "江之岛_clips")
PKGDIR = str(pkg_dir("江之岛"))
os.makedirs(OUT, exist_ok=True)

# ── Clip definitions ─────────────────────────────────────────────────────────
CLIPS = {
    # 精华版：全片最强五帧串烧
    "01_highlight": {
        "title": "大雨の江の島 精華版",
        "segments": [
            (2350, 2410),  # 39:10-40:10  海岸岩石+大浪+雨雾 ★★★ HOOK Kano#1
            (300, 370),    # 05:00-06:10  江島神社+大雨+反光 ★★★ Kano#2
            (1760, 1820),  # 29:20-30:20  雨中森林小径
            (4170, 4230),  # 69:30-70:30  苔藓壁+雨水
            (4770, 4820),  # 79:30-80:20  赤い小屋+石阶
        ],
        # 60+70+60+60+50 = 300s = 5:00 稍超 → trim 最后段
        # 60+70+60+60+40 = 290s ≈ 4:50
    },
    # 江島神社+参道
    "02_jinja": {
        "title": "雨の江島神社",
        "segments": [
            (300, 400),    # 05:00-06:40  神社正殿+大雨 ★★★ HOOK
            (60, 140),     # 01:00-02:20  参道入口+石阶
            (400, 470),    # 06:40-07:50  神社奥殿
            (500, 560),    # 08:20-09:20  参道上部
        ],
        # 100+80+70+60 = 310s 超 → trim
        # 90+80+70+60 = 300s → (300, 390)
        # 改为 80+80+70+50 = 280s ✓
    },
    # 海岸+岩石+大浪
    "03_umi": {
        "title": "荒波の岩場",
        "segments": [
            (2350, 2430),  # 39:10-40:30  海岸岩石+大浪 ★★★ HOOK
            (2200, 2280),  # 36:40-38:00  海岸接近+階段
            (2430, 2510),  # 40:30-41:50  岩場続き
            (5350, 5410),  # 89:10-90:10  海岸線+松
        ],
        # 80+80+80+60 = 300s → trim
        # 80+80+70+50 = 280s ✓
    },
    # 雨の路地+苔+緑
    "04_ame": {
        "title": "雨の路地",
        "segments": [
            (4170, 4240),  # 69:30-70:40  苔藓壁+雨 ★★★ HOOK
            (1760, 1830),  # 29:20-30:30  森林小径
            (2950, 3020),  # 49:10-50:20  巷弄+石阶
            (4770, 4830),  # 79:30-80:30  赤い小屋+緑
        ],
        # 70+70+70+60 = 270s = 4:30 ✓
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
    # 重编码 H.264 30fps + 竖屏裁切（去水印 + 抖音原生规格）
    run(f'ffmpeg -y -f concat -safe 0 -i "{list_path}" '
        f'-vf "crop=810:1440:875:0,scale=1080:1920" '
        f'-c:v libx264 -crf 18 -preset fast -r 30 '
        f'-c:a aac -b:a 192k "{merged_path}" 2>/dev/null')
    return merged_path

def extract_covers(merged_path, cover_dir):
    os.makedirs(cover_dir, exist_ok=True)
    for t in [3, 15, 30, 60, 90, 120]:
        run(f'ffmpeg -y -ss {t} -i "{merged_path}" -frames:v 1 '
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

    print("  剪辑合并（含竖屏裁切）...")
    cut_and_merge(segments, merged, clip_dir)

    # merged 已经是竖屏 1080x1920，直接作为 final
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

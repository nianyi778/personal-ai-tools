#!/usr/bin/env python3
"""Batch process 高野山 — 環境音版（奥の院・苔・石仏）"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT, pkg_dir

VIDEO  = str(PROJECT_ROOT / "高野山.mp4")
OUT    = str(PROJECT_ROOT / "高野山_clips")
PKGDIR = str(PROJECT_ROOT / "📦発布包" / "高野山")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PKGDIR, exist_ok=True)

# ── 全片扫描结论 ───────────────────────────────────────────────
# 素材：４K HDR 高野山 苔むす雨の奥の院（9分19秒，1080p，環境音のみ）
# URL：https://www.youtube.com/watch?v=WDNMMls4jUY
# 水印：无
# 音频：纯环境音（雨声+脚步+自然）
# 路线：奥の院参道（鸟居→石灯笼→地藏像→古寺）
# 画质：1080p（原片无4K，放宽规则使用）
#
# 场景分布：
#   0-55s    鸟居+石塔+苔藓，静谧开篇
#   55-157s  杉树深林+地藏像+红围巾
#   157-223s ⭐ 雨中参道+石灯笼排列+孤独人影（Kano帧）
#   223-280s 蕨类特写+苔藓细节
#   280-335s 苔藓布满的石鸟居横梁
#   335-400s ⭐ 心形镂空石灯笼+地藏像（独特！）
#   400-503s 红围巾石佛群+石像侧面+杉树
#   503-559s 古寺建筑（有告示牌，部分避开）
#
# 01_highlight  高野山奥の院  ~4:04
#   HOOK: 157-215  雨中参道+石灯笼+人影  [58s]  ← 动态+雨天最佳钩子
#         0-60     鸟居+石塔开篇          [60s]
#         322-400  心形灯笼+地藏像        [78s]
#         437-485  石像群+杉树            [48s]
#   total: 244s = 4:04 ✓
#
# 02_koke  苔と石仏  ~3:48
#   HOOK: 217-270  蕨类+苔藓特写          [53s]  ← 绿色细节，悬念感
#         50-120   苔藓深林+地藏像        [70s]
#         270-325  苔藓横梁+石鸟居        [55s]
#         400-450  红围巾石佛             [50s]
#   total: 228s = 3:48 ✓

CLIPS = {
    "01_highlight": {
        "title": "高野山奥の院",
        "segments": [
            (157, 215),  # 2:37-3:35  雨中参道+石灯笼+孤独人影  HOOK
            (0,   60),   # 0:00-1:00  鸟居+石塔，苔藓开篇
            (322, 400),  # 5:22-6:40  心形镂空石灯笼+地藏像
            (437, 485),  # 7:17-8:05  石像群+杉树背景
        ],
    },
    "02_koke": {
        "title": "苔と石仏",
        "segments": [
            (217, 270),  # 3:37-4:30  蕨类特写+苔藓  HOOK
            (50,  120),  # 0:50-2:00  苔藓深林+地藏像
            (270, 325),  # 4:30-5:25  苔藓横梁+石鸟居
            (400, 450),  # 6:40-7:30  红围巾石佛
        ],
    },
}

# ── FFmpeg helpers ─────────────────────────────────────────────────────────
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

# ── Main ──────────────────────────────────────────────────────────────────
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

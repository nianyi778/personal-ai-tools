#!/usr/bin/env python3
"""Batch process 京都・嵐山大雨 — 環境音版

素材：Drifted Films `Ilj8rSAaHzY` (78min, 嵐山大雨步行)
像素自检：底部 100px 近白像素均 0.0%（远低于 30% 阈值）✓
频道：Drifted Films（不在黑名单）✓
音频：纯环境音（雨声/脚步/溪流），mean -30dB, CV 0.07 ✓

策略：高认知度地名 + 雨天差异化 + 中文标题
- 3-5min 体裁（4min × 3条 = 12min 总产出）
- ★★★★★ 认知度（#京都 #嵐山 = 华人搜索热词）
- 雨天 HOOK = 账号最强跳出率杀手（实测跳出 33-40%）
- 竹林大雨段 = 视觉辨识度最高（绿色 59%）
- 中文标题：「雨天的嵐山，一个人也没有」
- ⚠️ 48min 暗隧道段(90% dark) 不做 HOOK（跳出率风险）
- ⚠️ 开场 0-6min 可能有片头/介绍，跳过
"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT

VIDEO  = str(PROJECT_ROOT / "京都・嵐山大雨.mp4")
OUT    = str(PROJECT_ROOT / "京都・嵐山大雨_clips")
PKGDIR = str(PROJECT_ROOT / "📦発布包" / "京都・嵐山大雨")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PKGDIR, exist_ok=True)

# ── 全片掃描結論 ───────────────────────────────────────────────
# Zone A 入口/桥 0-400s: 桥/渡口/街道 ✓（但非核心段）
#   - 362s 入口附近 green=17% ✓
# Zone B 街道/河岸 400-1700s: 嵐山街区 ✓（中等素材）
#   - 1084s 河岸街道 ✓
#   - 1448s 街区雨景 ✓
# Zone C 竹林核心 1700-2700s: ⭐⭐⭐ 最具辨识度
#   - 1810s 竹林开始 green=14% ✓
#   - 2172s 竹林深处 green=59% ⭐⭐⭐ ← Kano 惊喜帧
#   - 2535s 雨+竹+暖光 warm=11% ⭐⭐
# Zone D 暗/隧道 2700-3000s: ⚠️ 暗段（跳出率风险）
#   - 2897s 极暗隧道 dark=90% ⚠️ 不做 HOOK
# Zone E 街区+黄昏 3000-4000s: ⭐⭐
#   - 3259s 雨后街区 ✓
#   - 3621s 暗森林小径 dark=57% ⭐（可控暗度）
#   - 3983s 黄昏灯笼 warm=13% ⭐⭐
# Zone F 傍晚竹林 4000-4708s: ⭐⭐
#   - 4345s 竹林暖光 green=20% warm=11% ⭐⭐

CLIPS = {
    "01_highlight": {
        "title": "嵐山精華",
        "segments": [
            (2172, 2232),  # 36:12-37:12 🎋竹林深处·大雨 ⭐⭐⭐ HOOK
            (2535, 2595),  # 42:15-43:15 🎋雨+竹+暖光
            (3983, 4043),  # 66:23-67:23 🏮黄昏灯笼
            (1084, 1144),  # 18:04-19:04 🌊河岸街道·雨景
        ],
    },
    "02_bamboo": {
        "title": "竹林の雨",
        "segments": [
            (2172, 2232),  # 36:12-37:12 🎋竹林深处 HOOK
            (2232, 2292),  # 37:12-38:12 🎋竹林续段
            (2535, 2595),  # 42:15-43:15 🎋雨+竹+暖光
            (1810, 1870),  # 30:10-31:10 🎋竹林入口
        ],
    },
    "03_yuugure": {
        "title": "嵐山の夕暮れ",
        "segments": [
            (3983, 4043),  # 66:23-67:23 🏮黄昏灯笼·HOOK
            (4345, 4405),  # 72:25-73:25 🎋🏮竹林暖光
            (3621, 3681),  # 60:21-61:21 🌧️暗森林小径
            (1448, 1508),  # 24:08-25:08 🏠街区雨景
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
if not os.path.exists(VIDEO):
    print(f"❌ 视频文件不存在：{VIDEO}")
    print("   请先完成 yt-dlp 下载")
    sys.exit(1)

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
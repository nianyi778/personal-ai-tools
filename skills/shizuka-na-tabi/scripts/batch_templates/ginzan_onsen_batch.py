#!/usr/bin/env python3
"""Batch process 銀山温泉 — 環境音版

素材：Japan Travel Walk `CObbrqClkug` (55min, 4 segments: daytime/evening lamps/snowy night/morning snow)
像素自检：底部 100px 近白像素均 0.0%（远低于 30% 阈值）✓
频道：Japan Travel Walk（不在黑名单）✓
音频：纯环境音（雪声/脚步/溪流），mean -39.9dB ✓

策略：对标千与千寻联想 + 雪夜煤气灯 HOOK
- 3-5min 体裁（4min × 3条 = 12min 总产出）
- 高认知度 IP 地名（#銀山温泉 = 千与千寻联想）
- 雪夜煤气灯 = 动态夜景 HOOK（符合账号规律）
- 早朝大雪段 = 誰もいない差异化
- 白天游客段（3:00/5:00/9:00/12:00/15:00-18:00）全部跳过
"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT

VIDEO  = str(PROJECT_ROOT / "銀山温泉.mp4")
OUT    = str(PROJECT_ROOT / "銀山温泉_clips")
PKGDIR = str(PROJECT_ROOT / "📦発布包" / "銀山温泉")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PKGDIR, exist_ok=True)

# ── 全片掃描結論 ───────────────────────────────────────────────
# Zone A 开场 0-460s: 片头+少量游客 ✗ 跳过（3:00/5:00 有游客）
#   - 240s 雪景无人段 ✓（仅此段可用）
# Zone B 白天漫步 460-1489s: 游客密集段
#   - 9:00/12:00/15:00-18:00 游客扎堆 ✗
#   - 10:00-11:00/13:00-14:00/19:00-20:00 间歇无人 ✓（但不够稀缺）
# Zone C 傍晚灯笼 1489-2520s: ⭐⭐⭐ 最具辨识度
#   - 1500s 灯笼初亮（warm=44.5%）⭐⭐⭐
#   - 1800s 灯笼全亮 + 雪景 ⭐
#   - 2100s 深巷灯笼 ⭐
#   - 2400s 渐暗段 ⚠️（偏暗，限用）
# Zone D 雪夜 2520-2820s: ⭐⭐⭐ 最强 HOOK
#   - 2520s 煤气灯+飘雪开始 ⭐⭐⭐ ← Kano 惊喜帧
#   - 2580s 雪夜深巷 ⭐
#   - 2640s 雪夜续段 ⭐
#   - 2700s 雪夜最深处 ⭐
#   - 2760s 黎明前 ⚠️
# Zone E 早朝大雪 2820-3293s: ⭐⭐ 誰もいない
#   - 2820s 早朝大雪·旅馆街无人 ⭐⭐ ← HOOK for 03_akatsuki
#   - 2880s 早朝续段 ⭐
#   - 2940s 早朝续 ✓
#   - 3060s 早晨渐亮 ✓
#   - 3120s 早晨 ✓
# 40:00-41:40 过渡段 ✗（旅馆室内，跳过）

CLIPS = {
    "01_highlight": {
        "title": "銀山温泉精華",
        "segments": [
            (2520, 2580),  # 42:00-43:00  ❄️ 雪夜漫步·煤气灯+飘雪  HOOK
            (1500, 1560),  # 25:00-26:00  🏮 傍晚灯笼初亮
            (2700, 2760),  # 45:00-46:00  ❄️ 雪夜续段·深巷
            (2880, 2940),  # 48:00-49:00  🌅 早朝大雪·旅馆街无人
        ],
    },
    "02_yukiyo": {
        "title": "雪夜の灯",
        "segments": [
            (2520, 2580),  # 42:00-43:00  ❄️ 雪夜漫步  HOOK
            (2580, 2640),  # 43:00-44:00  雪夜续段
            (2640, 2700),  # 44:00-45:00  雪夜深段
            (2700, 2760),  # 45:00-46:00  雪夜最深处
        ],
    },
    "03_akatsuki": {
        "title": "朝の雪",
        "segments": [
            (2820, 2880),  # 47:00-48:00  🌅 早朝大雪·誰もいない  HOOK
            (2880, 2940),  # 48:00-49:00  早朝旅馆街
            (2940, 3000),  # 49:00-50:00  早朝续段
            (240, 300),    # 4:00-5:00   白天雪景无人段
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
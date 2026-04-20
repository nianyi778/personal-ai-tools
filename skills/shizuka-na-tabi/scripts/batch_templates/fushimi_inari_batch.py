#!/usr/bin/env python3
"""Batch process 伏見稲荷 千本鳥居 — 環境音版

素材：Scenery of Japan `pggb97tSmWU` (93min, 早朝 Senbon Torii approach)
像素自检：底部 100px 近白像素均 2.1%（远低于 30% 阈值）✓
目视验证：鳥居深处段（2400-3200s）完全无人 ✓

策略：对标奈良井宿爆款公式（21129 播 +250 粉）
- 3-5min 体裁
- 中高认知度地名（#伏見稲荷 #京都 #千本鳥居）
- 情绪化动词标题（「まだ誰もいない頃、～」）
- 前 5s Hook 用招牌帧（3000s 处对称鳥居隧道）
"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT

VIDEO  = str(PROJECT_ROOT / "伏見稲荷.mp4")
OUT    = str(PROJECT_ROOT / "伏見稲荷_clips")
PKGDIR = str(PROJECT_ROOT / "📦発布包" / "伏見稲荷")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PKGDIR, exist_ok=True)

# ── 全片掃描結論 ───────────────────────────────────────────────
# Zone A 入口 0-500s: 游客扎堆 ✗ 淘汰
# Zone B 末社 900-1300s: 零星游客 ⚠️ 限用
# Zone C 核心 2400-3200s: 鳥居深处，完全无人 ⭐⭐⭐
#   - 2460s 鳥居石阶延伸 (无人) ⭐
#   - 2520s 小神社红灯笼 (暗绿奥行) ⭐
#   - 2580s 鳥居仰视 (森林包围) ⭐
#   - 2640s 苔石阶 ✓
#   - 2880s 鳥居+石头地面 ✓
#   - 3000s ⭐⭐⭐ 招牌帧（对称鳥居隧道）← Kano 惊喜帧
#   - 3120s 鳥居石阶续段 ✓
# Zone D 奥社門 3400-3700s:
#   - 3460s 鳥居隧道+奉納字 ⭐
# Zone E 山中 4400-5200s:
#   - 4500s 山中鳥居+石碑 ✓
#   - 5000s 小神社+石灯笼 ✓
# 4049s 山頂俯瞰 ✗ 淘汰（都市景+游客扎堆）

CLIPS = {
    "01_highlight": {
        "title": "千本鳥居精華",
        "segments": [
            (3000, 3060),  # 50:00-51:00  ⭐⭐⭐ 招牌帧·对称鳥居隧道  HOOK
            (2460, 2520),  # 41:00-42:00  鳥居石阶延伸，无人
            (2880, 2940),  # 48:00-49:00  鳥居仰视+石头地面
            (3460, 3520),  # 57:40-58:40  奥社鳥居+奉納字清晰
        ],
    },
    "02_yami": {
        "title": "鳥居の奥の静寂",
        "segments": [
            (2520, 2580),  # 42:00-43:00  小神社红灯笼（奥行感）  HOOK
            (4500, 4560),  # 75:00-76:00  山中鳥居+石碑（末社孤寂）
            (2640, 2700),  # 44:00-45:00  苔石阶（奥院氛围）
            (5000, 5060),  # 83:20-84:20  小神社+石灯笼（结尾）
        ],
    },
    "03_green": {
        "title": "緑の奥の鳥居",
        "segments": [
            (2580, 2640),  # 43:00-44:00  鳥居仰视+森林包围  HOOK
            (3060, 3120),  # 51:00-52:00  鳥居石阶延续
            (3120, 3180),  # 52:00-53:00  鳥居石阶后续+地面质感
            (2400, 2460),  # 40:00-41:00  绿中小神社（结尾）
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
        # -c copy 快速切（对齐关键帧会略有漂移，可接受）
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

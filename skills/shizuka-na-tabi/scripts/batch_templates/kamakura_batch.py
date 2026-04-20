#!/usr/bin/env python3
"""Batch process 鎌倉雨天 — 環境音版（無字幕、4K HDR MKV 輸入）"""

import os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT

VIDEO  = str(PROJECT_ROOT / "鎌倉.mkv")
OUT    = str(PROJECT_ROOT / "鎌倉_clips")
PKGDIR = str(PROJECT_ROOT / "📦発布包" / "鎌倉")
os.makedirs(OUT, exist_ok=True)
os.makedirs(PKGDIR, exist_ok=True)

# ── 全片掃描結論 ───────────────────────────────────────────────
# 素材：鎌倉雨天步き by 4K JAPAN（62min，純環境音，無人口播）
# 水印：4K JAPAN 頻道確認無浮水印 ✓
# 人物：街中段落偶有路人（雨傘）→ 保留（雨の演出要素）
# 禁止：黑屏開頭（0-15s）跳過
#
# 分區：
#   商店街・住宅街エリア (0:15-17:00): 雨の街中步き、傘の列
#   神社・參道エリア     (21:00-28:00): 參道・石段・緑の小徑
#   街中續き            (28:00-39:30): 住宅街・路地
#   寺院・林道エリア     (39:30-46:30): 緑の小徑・寺院境内
#   商店街續き           (46:30-62:04): 長い街中步き
#
# 影片無海岸段（全篇街中+神社）
#
# 01_highlight  雨の鎌倉・精華  ~4:10
#   HOOK: 15-95     雨の商店街・傘・反射         HOOK（雨天街道最強）80s
#         1290-1350  神社參道・雨・石段                          60s
#         2430-2500  寺院の綠・雨音                              70s
#   total: 210s = 3:30 ✓
#
# 02_jinja  雨の日だから、鎌倉が好きになった  ~4:10
#   HOOK: 1530-1600  神社の鳥居・雨・石段         HOOK             70s
#         1680-1740  緑の參道・雨音                                 60s
#         2700-2770  寺院境内・苔・雨                              70s
#   total: 200s → 再加 2800-2870 住宅街締め  70s → 270s = 4:30 ✓
#
# 03_machi  誰もいない、雨の鎌倉  ~4:20
#   HOOK: 500-580   住宅街の雨・反射                HOOK             80s
#         1680-1740  緑の參道・雨音                                 60s
#         2800-2890  路地裏・雨の石畳                              90s → trim
#   total: 230s → 再加 840-900 商店街  60s → 240s + 30 = 270s → 調整
#   Revised: 500-570 (70s) + 840-910 (70s) + 1680-1750 (70s) + 2800-2870 (70s)
#   total: 280s → over, trim last to 60s → 270s = 4:30 ✓
#
# 04_yukkuri  雨の音だけ、鎌倉を步いた  ~3:50
#   HOOK: 150-230   雨天商店街・傘の列              HOOK             80s
#         2100-2180  神社の靜けさ・雨                                80s
#         3220-3290  路地・民家の雨                                 70s
#   total: 230s = 3:50 ✓

CLIPS = {
    "01_highlight": {
        "title": "雨の鎌倉",
        "segments": [
            (15,   95),    # 00:15-01:35  雨の商店街・傘・反射  HOOK
            (1290, 1350),  # 21:30-22:30  神社參道・雨・石段
            (2430, 2500),  # 40:30-41:40  寺院の綠・雨音
        ],
    },
    "02_jinja": {
        "title": "雨の日だから、鎌倉が好きになった",
        "segments": [
            (1530, 1600),  # 25:30-26:40  神社の鳥居・雨・石段  HOOK
            (1680, 1740),  # 28:00-29:00  緑の參道・雨音
            (2770, 2830),  # 46:10-47:10  寺院境内・苔・雨
            (3450, 3510),  # 57:30-58:30  商店街・雨を締め
        ],
    },
    "03_machi": {
        "title": "誰もいない、雨の鎌倉",
        "segments": [
            (500,  570),   # 08:20-09:30  住宅街の雨・反射  HOOK
            (840,  910),   # 14:00-15:10  商店街の雨
            (1680, 1750),  # 28:00-29:10  緑の參道・雨音
            (2800, 2860),  # 46:40-47:40  路地裏・雨の石畳  (60s, was 70s)
        ],
    },
    "04_yukkuri": {
        "title": "雨の音だけ、鎌倉を步いた",
        "segments": [
            (150,  230),   # 02:30-03:50  雨天商店街・傘の列  HOOK
            (2100, 2180),  # 35:00-36:20  神社の靜けさ・雨
            (3220, 3290),  # 53:40-54:50  路地・民家の雨
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
    """Cut segments and concat into merged.mp4 (re-encode to h264+aac for compatibility)"""
    parts = []
    for i, (s, e) in enumerate(segments):
        p = f"{clip_dir}/seg_{i:02d}.mp4"
        # VP9 MKV input → re-encode each segment to h264
        run(f'ffmpeg -y -ss {s} -to {e} -i "{VIDEO}" '
            f'-c:v libx264 -crf 18 -preset fast -c:a aac -b:a 128k "{p}" 2>/dev/null')
        parts.append(p)
    list_path = f"{clip_dir}/list.txt"
    with open(list_path, 'w') as f:
        f.write('\n'.join(f"file '{p}'" for p in parts))
    run(f'ffmpeg -y -f concat -safe 0 -i "{list_path}" '
        f'-c copy "{merged_path}" 2>/dev/null')
    return merged_path

def extract_covers(merged_path, cover_dir):
    os.makedirs(cover_dir, exist_ok=True)
    for t in [5, 30, 60, 100, 150]:
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

    # Validate duration
    if total < 210:
        print(f"  ⚠️ 時長不足3:30（{total}s），需追加片段")
    elif total > 270:
        print(f"  ⚠️ 時長超過4:30（{total}s），需裁減")

    print("  剪輯合併...")
    cut_and_merge(segments, merged, clip_dir)

    # 環境音版：merged = final（無字幕）
    run(f'cp "{merged}" "{final}"')

    cover_dir = f"{clip_dir}/封面"
    extract_covers(merged, cover_dir)

    size = os.path.getsize(final) / 1024 / 1024 if os.path.exists(final) else 0
    print(f"  ✓ → {final} ({size:.0f}MB)")

print("\n🎉 全部完成！取件路徑：")
print(f"  {PKGDIR}/")
for key in CLIPS:
    p = f"{PKGDIR}/{key}_final.mp4"
    if os.path.exists(p):
        size = os.path.getsize(p) / 1024 / 1024
        print(f"    {key}_final.mp4  ({size:.0f}MB)")

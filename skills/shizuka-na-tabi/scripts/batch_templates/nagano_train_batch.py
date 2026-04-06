"""Batch process 長野列車前方展望 (vFH2lGROUI8) — 無字幕・治愈系."""

import os
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed

VIDEO = "/Users/likai/Downloads/nagano_train.mp4"
OUT   = "/Users/likai/Downloads/nagano_train_clips"

os.makedirs(OUT, exist_ok=True)

# Key timestamps (sampled every 60s):
#   30s   緑の回廊（小ロゴあり）
#   80s~  ロゴ消える、緑の森
#  150s   水田・山々・開放的
#  760s   深緑の峡谷
#  810s   鉄橋
#  870s   緑トンネル
# 1050s   渓流・山腹
# 1110s   鉄橋
# 1830s   開けた緑の谷
# 2310s   急斜面の崖線路
# 2430s   広大な田園
# 2550s   ★最美: 信州平原・北アルプス全景
# 2670s   ★★最美: 水田・山・空
# 3690s   霧の森
# 3750s   山谷
# 3870s   静かな谷間
# 3990s   開けた緑

CLIPS = {
    "01_highlight": {
        "title": "精华版",
        # Hook: 最美水田全景 → 緑の回廊 → 深緑峡谷 → 霧の森
        "segments": [
            (2650, 2720),  # 44:10-45:20  ★HOOK: 信州平原・水田・北アルプス
            (80,   150),   # 1:20-2:30    緑の回廊（ロゴ消えた後）
            (760,  830),   # 12:40-13:50  深緑の峡谷・鉄橋
            (3700, 3770),  # 61:40-62:50  霧の緑の森
        ],
        # 総時長: 70+70+70+70 = 280s ≈ 4:40 ✓
    },
    "02_long": {
        "title": "沉浸长视频・夏の長野",
        # 緑の回廊 → 峡谷 → 信州平原（最美） → 山谷
        "segments": [
            (80,   210),   # 1:20-3:30    緑の回廊・田園の朝
            (760,  940),   # 12:40-15:40  峡谷・鉄橋・深緑の森
            (2560, 2730),  # 42:40-45:30  信州平原・水田・北アルプス（核心段落）
            (3690, 3940),  # 61:30-65:40  霧の山谷・静謐な夏の長野
        ],
        # 総時長: 130+180+170+250 = 730s ≈ 12:10 ✓
    },
}


# ── FFmpeg helpers ─────────────────────────────────────────────────────────

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERR: {result.stderr[-300:]}")
    return result.returncode == 0


def cut_and_merge(segments, merged_path, clip_dir):
    parts = []
    for i, (s, e) in enumerate(segments):
        p = f"{clip_dir}/seg_{i:02d}.mp4"
        run(f'ffmpeg -y -ss {s} -to {e} -i "{VIDEO}" -c copy "{p}" 2>/dev/null')
        parts.append(p)
    list_path = f"{clip_dir}/list.txt"
    with open(list_path, "w") as f:
        f.write("\n".join(f"file '{p}'" for p in parts))
    run(f'ffmpeg -y -f concat -safe 0 -i "{list_path}" -c copy "{merged_path}"')
    return merged_path


# ── Per-clip worker ────────────────────────────────────────────────────────

def process_clip(args):
    key, cfg = args
    title    = cfg["title"]
    segments = cfg["segments"]
    clip_dir  = f"{OUT}/{key}"
    video_dir = f"{clip_dir}/视频"
    cover_dir = f"{clip_dir}/封面"
    for d in [clip_dir, video_dir, cover_dir]:
        os.makedirs(d, exist_ok=True)

    total_sec = sum(e - s for s, e in segments)
    mm, ss = divmod(int(total_sec), 60)
    print(f"[{key}] {title}  时长 {mm}:{ss:02d}  ({len(segments)} 段)", flush=True)

    merged = f"{video_dir}/merged.mp4"
    cut_and_merge(segments, merged, clip_dir)

    # 无字幕：merged.mp4 直接作为最终成片
    final = f"{video_dir}/nagano_train_{key}_final.mp4"
    run(f'cp "{merged}" "{final}"')

    # 取封面帧
    for t in [5, 20, 40, 60, 80, 120]:
        frame_path = f"{cover_dir}/frame_{t:03d}s.png"
        run(f'ffmpeg -y -ss {t} -i "{merged}" -vframes 1 "{frame_path}" 2>/dev/null')

    print(f"  [{key}] ✓ → {clip_dir}/\n", flush=True)
    return key


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tasks = [(key, cfg) for key, cfg in CLIPS.items()]
    print(f"並行処理 {len(tasks)} 条...\n")

    with ProcessPoolExecutor(max_workers=len(tasks)) as ex:
        futs = {ex.submit(process_clip, t): t[0] for t in tasks}
        for f in as_completed(futs):
            key = futs[f]
            try:
                f.result()
            except Exception as e:
                print(f"  ✗ [{key}] 出错: {e}")

    print("全部完成 ✓")

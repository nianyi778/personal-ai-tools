#!/usr/bin/env python3
"""上高地 · 4 条封面生成"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from make_covers import generate_covers
from config import PROJECT_ROOT

NAME = "上高地"
CLIPS_DIR = PROJECT_ROOT / f"{NAME}_clips"

COVERS = [
    {
        "key": "01_highlight",
        "frame": str(CLIPS_DIR / "01_highlight/封面_v/frame_15s.png"),
        "top_label": "KAMIKOCHI · AUTUMN DAWN",
        "main_title": "上高地",
        "sub_title": "Before dawn, no one was there",
        "mood": [
            "AM5:00、梓川の向こうに穂高が立っていた。",
            "川の音だけが、朝の静けさを満たしていた。",
            "ただ、紅葉の道を歩いた。",
        ],
        "episode": "Episode 01 · Highlight",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.85) brightness(0.80)",
    },
    {
        "key": "02_akatsuki",
        "frame": str(CLIPS_DIR / "02_akatsuki/封面_v/frame_15s.png"),
        "top_label": "KAMIKOCHI · DAYBREAK",
        "main_title": "夜明け",
        "sub_title": "AM5:00, the mountain was still asleep",
        "mood": [
            "月がまだ空にあった、梓川の朝。",
            "山が少しずつ、赤く目を覚ましていった。",
            "誰もいなかった。それでよかった。",
        ],
        "episode": "Episode 02 · Akatsuki",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.85) brightness(0.88)",
    },
    {
        "key": "03_shitsugen",
        "frame": str(CLIPS_DIR / "03_shitsugen/封面_v/frame_15s.png"),
        "top_label": "KAMIKOCHI · WETLAND",
        "main_title": "湿原",
        "sub_title": "A wooden path through the morning marsh",
        "mood": [
            "穂高連峰の麓、色づいた草原を、木道が貫いていた。",
            "池の水は、昨日の星を映したまま眠っていた。",
            "ただ、一人で歩いた。",
        ],
        "episode": "Episode 03 · Shitsugen",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.72) brightness(0.70)",
    },
    {
        "key": "04_koyo",
        "frame": str(CLIPS_DIR / "04_koyo/封面_v/frame_60s.png"),
        "top_label": "KAMIKOCHI · AUTUMN",
        "main_title": "紅葉",
        "sub_title": "Only this place has this color",
        "mood": [
            "橙、黄、紅。杉の緑が混ざり、道は秋になっていた。",
            "落ち葉を踏む音だけが、森に響いていた。",
            "この道を、誰かと歩きたかった。",
        ],
        "episode": "Episode 04 · Koyo",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.85) brightness(0.78)",
    },
]

if __name__ == "__main__":
    print(f"生成 {len(COVERS)} 张封面...")
    results = generate_covers(NAME, COVERS)
    print(f"\n🎉 完成 {len(results)} 张")
    for r in results:
        print(f"  → {r}")

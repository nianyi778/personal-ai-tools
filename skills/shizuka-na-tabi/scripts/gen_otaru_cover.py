#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from make_covers import generate_covers

COVERS = [
    {
        "key": "01_highlight",
        "frame": "/Users/likai/personage/personal-ai-tools/skills/shizuka-na-tabi/小樽_clips/01_highlight/封面/frame_060s.png",
        "top_label": "OTARU · WINTER",
        "main_title": "小樽",
        "sub_title": "Snow fell on the old canal",
        "mood": ["雪が降り続く", "運河の水面が凍る", "誰もいない"],
        "episode": "Episode 01 · Highlight",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.55) brightness(0.65)",
    }
]

generate_covers("小樽", COVERS)

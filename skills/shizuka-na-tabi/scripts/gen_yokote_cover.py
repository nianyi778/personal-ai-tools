#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from make_covers import generate_covers

COVERS = [
    {
        "key": "01_highlight",
        "frame": "/Users/likai/personage/personal-ai-tools/skills/shizuka-na-tabi/横手城_clips/01_highlight/封面/frame_060s.png",
        "top_label": "YOKOTE · WINTER",
        "main_title": "横手城下町",
        "sub_title": "Snow fell on the old castle town",
        "mood": ["雪が積もっていた", "鳥居の朱色が燃えていた", "誰もいなかった"],
        "episode": "Episode 01 · Highlight",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.55) brightness(0.65)",
    },
    {
        "key": "02_jinja",
        "frame": "/Users/likai/personage/personal-ai-tools/skills/shizuka-na-tabi/横手城_clips/02_jinja/封面/frame_030s.png",
        "top_label": "YOKOTE · WINTER",
        "main_title": "雪の神社",
        "sub_title": "Only the torii gate was vermillion",
        "mood": ["鳥居の下で雪が積もっていた", "手水舎の水音が響いた", "参道の先に誰もいなかった"],
        "episode": "Episode 02 · Shrine",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.55) brightness(0.65)",
    },
    {
        "key": "03_castle",
        "frame": "/Users/likai/personage/personal-ai-tools/skills/shizuka-na-tabi/横手城_clips/03_castle/封面/frame_030s.png",
        "top_label": "YOKOTE · WINTER",
        "main_title": "横手城",
        "sub_title": "The castle was surrounded by snow",
        "mood": ["天守閣で雪が舞っていた", "白い庭園が広がっていた", "時代が止まっていた"],
        "episode": "Episode 03 · Castle",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.55) brightness(0.65)",
    }
]

generate_covers("横手城", COVERS)

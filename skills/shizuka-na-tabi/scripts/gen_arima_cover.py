#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from make_covers import generate_covers

COVERS = [
    {
        "key": "01_highlight",
        "frame": "/Users/likai/personage/personal-ai-tools/skills/shizuka-na-tabi/有馬温泉_clips/01_highlight/封面/frame_060s.png",
        "top_label": "ARIMA · ONSEN",
        "main_title": "有馬温泉",
        "sub_title": "Steam rose from the old town",
        "mood": ["温泉街に蒸汽が立っていた", "古い建物が並んでいた", "誰もいなかった"],
        "episode": "Episode 01 · Highlight",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.65) brightness(0.75)",
    },
    {
        "key": "02_steam",
        "frame": "/Users/likai/personage/personal-ai-tools/skills/shizuka-na-tabi/有馬温泉_clips/02_steam/封面/frame_030s.png",
        "top_label": "ARIMA · ONSEN",
        "main_title": "奥の道",
        "sub_title": "The mountain path was quiet",
        "mood": ["山道が静かだった", "緑に囲まれていた", "足音だけが響いた"],
        "episode": "Episode 02 · Path",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.65) brightness(0.70)",
    }
]

generate_covers("有馬温泉", COVERS)

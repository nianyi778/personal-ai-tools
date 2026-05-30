#!/usr/bin/env python3
"""东京雨夜 · 4 条封面生成"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT
from make_covers import generate_covers

CLIPS_DIR = PROJECT_ROOT / "东京雨夜_clips"

COVERS = [
    {
        "key": "01_day_rain",
        "frame": str(CLIPS_DIR / "01_day_rain" / "封面" / "frame_060s.png"),
        "top_label": "TOKYO · DAY RAIN",
        "main_title": "東京駅",
        "sub_title": "Rain came to the city",
        "mood": [
            "雨が、東京駅の前に降り始めた。",
            "傘の音だけが、湿った石畳を歩いた。",
            "誰も急いでいなかった。",
        ],
        "episode": "Episode 01 · Day Rain",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.75) brightness(0.85)",
    },
    {
        "key": "02_dusk_transition",
        "frame": str(CLIPS_DIR / "02_dusk_transition" / "封面" / "frame_030s.png"),
        "top_label": "TOKYO · DUSK",
        "main_title": "黄昏",
        "sub_title": "One by one, lanterns lit up",
        "mood": [
            "街灯がひとつ、またひとつ灯った。",
            "居酒屋の暖簾が、雨に濡れていた。",
            "夜が、東京を包んでいく。",
        ],
        "episode": "Episode 02 · Dusk",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.85) brightness(0.85)",
    },
    {
        "key": "04_ginza_deep",
        "frame": str(CLIPS_DIR / "04_ginza_deep" / "封面" / "frame_015s.png"),
        "top_label": "GINZA · RAIN NIGHT",
        "main_title": "銀座",
        "sub_title": "No one looked at the windows",
        "mood": [
            "雨の銀座、傘ばかりが流れていた。",
            "ショーウィンドウの灯、誰も見ていなかった。",
            "ただ、静かに通り過ぎた。",
        ],
        "episode": "Episode 03 · Ginza Rain",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.75) brightness(0.85)",
    },
    {
        "key": "10_tokyo_tower",
        "frame": str(CLIPS_DIR / "10_tokyo_tower" / "封面" / "frame_060s.png"),
        "top_label": "TOKYO TOWER · RAIN",
        "main_title": "東京タワー",
        "sub_title": "Red lights bled in the rain",
        "mood": [
            "鉄骨の下、雨が降り続けていた。",
            "赤いテールライトが、路面に滲んでいた。",
            "東京タワーの下、ただ立っていた。",
        ],
        "episode": "Episode 04 · Tokyo Tower",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.85) brightness(0.80)",
    },
]


if __name__ == "__main__":
    results = generate_covers("东京雨夜", COVERS)
    print(f"\n✓ 生成 {len(results)} 张封面")
    for p in results:
        print(f"  {p}")

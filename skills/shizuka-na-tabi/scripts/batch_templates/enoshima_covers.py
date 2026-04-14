#!/usr/bin/env python3
"""江之岛 · 4 条封面生成"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from make_covers import generate_covers
from config import PROJECT_ROOT

NAME = "江之岛"
CLIPS_DIR = PROJECT_ROOT / f"{NAME}_clips"

COVERS = [
    {
        "key": "01_highlight",
        "frame": str(CLIPS_DIR / "01_highlight/封面/frame_060s.png"),
        "top_label": "ENOSHIMA · HEAVY RAIN",
        "main_title": "江の島",
        "sub_title": "No one was there in the heavy rain",
        "mood": [
            "波が岩を砕く音だけが、霧の中に響いていた。",
            "石畳が光っていた。雨だけが、この島を歩いていた。",
            "ただ、濡れながら歩いた。",
        ],
        "episode": "Episode 01 · Highlight",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.75) brightness(0.85)",
    },
    {
        "key": "02_jinja",
        "frame": str(CLIPS_DIR / "02_jinja/封面/frame_015s.png"),
        "top_label": "ENOSHIMA · SHRINE",
        "main_title": "江島神社",
        "sub_title": "The rain was the only prayer",
        "mood": [
            "石段を上がると、誰もいない拝殿があった。",
            "雨が屋根を叩く音だけが、参道に響いていた。",
            "ここに来てよかった、と思った。",
        ],
        "episode": "Episode 02 · Jinja",
        "bg_pos": "center 60%",
        "bg_filter": "saturate(0.72) brightness(0.78)",
    },
    {
        "key": "03_umi",
        "frame": str(CLIPS_DIR / "03_umi/封面/frame_003s.png"),
        "top_label": "ENOSHIMA · SHORE",
        "main_title": "荒波",
        "sub_title": "Beyond the waves, nothing was visible",
        "mood": [
            "岩場に立つと、足元まで波が来た。",
            "雨と潮が混ざって、世界が灰色になっていた。",
            "それでも、ずっと見ていた。",
        ],
        "episode": "Episode 03 · Umi",
        "bg_pos": "center 40%",
        "bg_filter": "saturate(0.78) brightness(0.80)",
    },
    {
        "key": "04_ame",
        "frame": str(CLIPS_DIR / "04_ame/封面/frame_015s.png"),
        "top_label": "ENOSHIMA · ALLEY",
        "main_title": "雨の路地",
        "sub_title": "The moss wall kept collecting the rain",
        "mood": [
            "路地裏の石段を、水が流れ落ちていた。",
            "緑が雨に濡れて、色が深くなっていた。",
            "この道を、誰も歩いていなかった。",
        ],
        "episode": "Episode 04 · Ame",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(0.80) brightness(0.82)",
    },
]

if __name__ == "__main__":
    print(f"生成 {len(COVERS)} 张封面...")
    results = generate_covers(NAME, COVERS)
    print(f"\n🎉 完成 {len(results)} 张")
    for r in results:
        print(f"  → {r}")

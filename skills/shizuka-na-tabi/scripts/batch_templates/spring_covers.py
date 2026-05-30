#!/usr/bin/env python3
"""4 套素材封面批生成 — 草津 / 熊野 / 尾道 / 角館"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT
from make_covers import generate_covers

CLIPS_DIR = PROJECT_ROOT

ALL_COVERS = {
    "草津温泉": [
        {
            "key": "01_highlight",
            "frame": str(CLIPS_DIR / "草津温泉_clips/01_highlight/封面/frame_030s.png"),
            "top_label": "KUSATSU · WINTER NIGHT",
            "main_title": "草津",
            "sub_title": "The lanterns came on in the snow",
            "mood": [
                "雪の夜、湯畑に灯が灯った。",
                "蒸気が、街の上を流れていった。",
                "ただ、静かに見ていた。",
            ],
            "episode": "Episode 01 · Yu-batake",
            "bg_pos": "center 50%",
            "bg_filter": "saturate(0.85) brightness(0.80)",
        },
        {
            "key": "02_yoru",
            "frame": str(CLIPS_DIR / "草津温泉_clips/02_yoru/封面/frame_030s.png"),
            "top_label": "KUSATSU · DUSK",
            "main_title": "夕暮れ",
            "sub_title": "The town lit up one lamp at a time",
            "mood": [
                "雪の上に、街灯がともった。",
                "車も人も、まだ眠っていた。",
                "ただ、雪の街を歩いた。",
            ],
            "episode": "Episode 02 · Evening Walk",
            "bg_pos": "center 50%",
            "bg_filter": "saturate(0.75) brightness(0.85)",
        },
    ],
    "熊野古道": [
        {
            "key": "01_highlight",
            "frame": str(CLIPS_DIR / "熊野古道_clips/01_highlight/封面/frame_030s.png"),
            "top_label": "KUMANO KODO · RAIN",
            "main_title": "熊野古道",
            "sub_title": "Stone steps under a thousand years of moss",
            "mood": [
                "苔の上に、雨が降り続いていた。",
                "千年前の石段を、ただ登った。",
                "誰とも、すれ違わなかった。",
            ],
            "episode": "Episode 01 · Ancient Path",
            "bg_pos": "center 50%",
            "bg_filter": "saturate(0.85) brightness(0.85)",
        },
        {
            "key": "02_kodo",
            "frame": str(CLIPS_DIR / "熊野古道_clips/02_kodo/封面/frame_030s.png"),
            "top_label": "KUMANO · CEDAR PATH",
            "main_title": "杉並木",
            "sub_title": "Trees that have stood for centuries",
            "mood": [
                "杉の木に、雨が落ちていた。",
                "古道の石畳、足音だけ。",
                "森が、静かに見守っていた。",
            ],
            "episode": "Episode 02 · Cedar Forest",
            "bg_pos": "center 50%",
            "bg_filter": "saturate(0.85) brightness(0.80)",
        },
        {
            "key": "03_taki",
            "frame": str(CLIPS_DIR / "熊野古道_clips/03_taki/封面/frame_090s.png"),
            "top_label": "NACHI · SACRED FALL",
            "main_title": "那智の滝",
            "sub_title": "Louder than the rain itself",
            "mood": [
                "雨の中、滝の音が響いていた。",
                "苔むした参道、静かに進んだ。",
                "千年前と、何も変わっていない。",
            ],
            "episode": "Episode 03 · Nachi Falls",
            "bg_pos": "center 50%",
            "bg_filter": "saturate(0.90) brightness(0.85)",
        },
    ],
    "尾道": [
        {
            "key": "01_highlight",
            "frame": str(CLIPS_DIR / "尾道_clips/01_highlight/封面/frame_030s.png"),
            "top_label": "ONOMICHI · MORNING",
            "main_title": "尾道",
            "sub_title": "The arcade was empty at dawn",
            "mood": [
                "朝の尾道、商店街に誰もいなかった。",
                "シャッターの音、自転車のベル。",
                "海が、すぐそこにあった。",
            ],
            "episode": "Episode 01 · Shōtengai",
            "bg_pos": "center 50%",
            "bg_filter": "saturate(0.75) brightness(0.85)",
        },
        {
            "key": "02_senkoji",
            "frame": str(CLIPS_DIR / "尾道_clips/02_senkoji/封面/frame_030s.png"),
            "top_label": "ONOMICHI · SENKO-JI",
            "main_title": "千光寺",
            "sub_title": "Every step shows you the sea",
            "mood": [
                "坂を登るたびに、海が見えた。",
                "瀬戸内の風、瓦屋根の街。",
                "ここで、時間が止まっていた。",
            ],
            "episode": "Episode 02 · Hilltop Temple",
            "bg_pos": "center 60%",
            "bg_filter": "saturate(0.75) brightness(0.80)",
        },
        {
            "key": "03_machi",
            "frame": str(CLIPS_DIR / "尾道_clips/03_machi/封面/frame_090s.png"),
            "top_label": "ONOMICHI · ALLEY",
            "main_title": "山陰小路",
            "sub_title": "Where time forgot to walk",
            "mood": [
                "細い路地、洗濯物が揺れていた。",
                "猫が一匹、塀の上に座っていた。",
                "尾道の時間は、ゆっくり流れる。",
            ],
            "episode": "Episode 03 · Alleyway",
            "bg_pos": "center 50%",
            "bg_filter": "saturate(0.70) brightness(0.85)",
        },
    ],
    "角館": [
        {
            "key": "01_highlight",
            "frame": str(CLIPS_DIR / "角館_clips/01_highlight/封面/frame_030s.png"),
            "top_label": "KAKUNODATE · SNOW NIGHT",
            "main_title": "角館",
            "sub_title": "Not a soul in the samurai town",
            "mood": [
                "雪が積もる夜、誰もいなかった。",
                "電線の影だけが、雪を渡っていた。",
                "ただ、足音を残していった。",
            ],
            "episode": "Episode 01 · Samurai Town",
            "bg_pos": "center 50%",
            "bg_filter": "saturate(0.85) brightness(0.85)",
        },
        {
            "key": "02_yakata",
            "frame": str(CLIPS_DIR / "角館_clips/02_yakata/封面/frame_030s.png"),
            "top_label": "KAKUNODATE · KUROBEI",
            "main_title": "黒板塀",
            "sub_title": "Snow falling on a 300-year-old wall",
            "mood": [
                "黒い板塀に、雪が降っていた。",
                "300年前の屋敷、今も静かに立っている。",
                "時代の音が、雪に吸い込まれた。",
            ],
            "episode": "Episode 02 · Black Walls",
            "bg_pos": "center 50%",
            "bg_filter": "saturate(0.85) brightness(0.80)",
        },
        {
            "key": "03_yuki",
            "frame": str(CLIPS_DIR / "角館_clips/03_yuki/封面/frame_030s.png"),
            "top_label": "KAKUNODATE · ONLY SNOW",
            "main_title": "雪の音",
            "sub_title": "Snow was the only thing falling",
            "mood": [
                "街灯の下、雪が降りていた。",
                "風もなく、犬も鳴かなかった。",
                "雪だけが、ずっと降っていた。",
            ],
            "episode": "Episode 03 · Silent Snow",
            "bg_pos": "center 50%",
            "bg_filter": "saturate(0.80) brightness(0.85)",
        },
    ],
}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", help="只处理指定素材")
    args = parser.parse_args()

    targets = args.only or list(ALL_COVERS.keys())
    for name in targets:
        if name not in ALL_COVERS:
            print(f"⚠️ 跳过未知素材: {name}")
            continue
        print(f"\n━━━━━ {name} ━━━━━")
        results = generate_covers(name, ALL_COVERS[name])
        print(f"✓ {len(results)} 张封面已生成")

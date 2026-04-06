#!/usr/bin/env python3
"""Generate Douyin covers (1080x1920) for Mitarai clips using Playwright."""

import base64, os
from playwright.sync_api import sync_playwright

def b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def mime(path):
    return "image/jpeg" if path.lower().endswith(('.jpg', '.jpeg')) else "image/png"

OUT_DIR = "/Users/likai/Downloads/mitarai_clips"

COVERS = [
    {
        "key": "01_highlight/封面/cover",
        "frame": "/tmp/mitarai_frames/01_highlight_t174.jpg",
        "top_label": "HIROSHIMA · MITARAI · WINTER",
        "main_title": "御手洗",
        "sub_title": "A port where winds once rested",
        "mood": [
            "江戸の息吹が、今も路地に漂っている。",
            "時間の流れが、ここだけ違う気がした。",
            "風待ちの港は、静かに美しかった。",
        ],
        "episode": "Episode 01 · Highlight",
        "bg_pos": "center 40%",
        "bg_filter": "saturate(0.85) brightness(0.60)",
    },
    {
        "key": "02_harbor/封面/cover",
        "frame": "/tmp/mitarai_frames/02_harbor_t94.jpg",
        "top_label": "HIROSHIMA · MITARAI · HARBOR",
        "main_title": "風待ち",
        "sub_title": "Where sailors prayed for the wind",
        "mood": [
            "石造りの灯台が、朝の光に溶けていた。",
            "住吉神社の鳥居は、海の向こうへ続いていた。",
            "波の音だけが、時を刻んでいた。",
        ],
        "episode": "Episode 02 · Harbor & Shrine",
        "bg_pos": "center 45%",
        "bg_filter": "saturate(0.75) brightness(0.55)",
    },
    {
        "key": "03_machinaka/封面/cover",
        "frame": "/tmp/mitarai_frames/03_machinaka_t260.jpg",
        "top_label": "HIROSHIMA · MITARAI · EDO ERA",
        "main_title": "路地裏",
        "sub_title": "Edo still breathes in these alleys",
        "mood": [
            "木格子、漆喰、入母屋の屋根。",
            "商人たちの誇りが、静かに残っていた。",
            "生活の気配が、心地よかった。",
        ],
        "episode": "Episode 03 · Town Exploration",
        "bg_pos": "center 35%",
        "bg_filter": "saturate(0.90) brightness(0.58)",
    },
    {
        "key": "04_ochou/封面/cover",
        "frame": "/tmp/mitarai_frames/04_ochou_t235.jpg",
        "top_label": "HIROSHIMA · OCHO · SETO INLAND SEA",
        "main_title": "大長",
        "sub_title": "A thousand islands, one quiet sea",
        "mood": [
            "瀬戸内の島々が、霞の中に浮かんでいた。",
            "みかん畑の向こうに、橋が架かっていた。",
            "この景色を、ずっと見ていたかった。",
        ],
        "episode": "Episode 04 · Ocho & Hilltop View",
        "bg_pos": "center 50%",
        "bg_filter": "saturate(1.05) brightness(0.62)",
    },
]

TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@200;300&family=Cormorant+Garamond:ital,wght@0,300;1,300&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:1080px; height:1920px; overflow:hidden; position:relative; }}
.bg {{
  position:absolute; inset:0;
  background: url('data:{mime};base64,{img}') {bg_pos} / cover no-repeat;
  filter: {bg_filter};
}}
.gradient-overlay {{
  position:absolute; inset:0; z-index:2;
  background: linear-gradient(to bottom,
    rgba(4,6,12,0.72) 0%, rgba(4,6,12,0.08) 22%,
    rgba(4,6,12,0.22) 38%, rgba(4,6,12,0.30) 50%, rgba(4,6,12,0.22) 62%,
    rgba(4,6,12,0.72) 78%, rgba(4,6,12,0.93) 100%);
}}
.content {{ position:absolute; inset:0; z-index:20; display:flex; flex-direction:column; align-items:center; }}
.top-label {{ margin-top:136px; font-family:'Cormorant Garamond',serif; font-style:italic; font-size:22px; color:rgba(148,163,176,0.82); letter-spacing:0.28em; }}
.top-rule {{ width:90px; height:1px; margin-top:18px; background:linear-gradient(to right,transparent,rgba(155,170,185,0.5),transparent); }}
.title-mask {{
  position:absolute; inset:0; pointer-events:none; z-index:5;
  background: radial-gradient(ellipse 80% 24% at 50% 46%,
    rgba(0,0,0,0.58) 0%,
    rgba(0,0,0,0.20) 55%,
    rgba(0,0,0,0.0) 100%);
}}
.title-block {{ margin-top:auto; transform:translateY(-545px); text-align:center; }}
.main-title {{ font-family:'Noto Serif JP',serif; font-weight:200; font-size:112px; color:rgba(248,244,234,0.97); letter-spacing:0.04em; text-shadow:0 2px 8px rgba(0,0,0,0.9), 0 4px 32px rgba(0,0,0,0.6), 0 0 60px rgba(0,0,0,0.4); line-height:1.08; }}
.mid-rule {{ width:175px; height:1px; margin:24px auto; background:linear-gradient(to right,transparent,rgba(178,193,206,0.58),transparent); }}
.sub-title {{ font-family:'Cormorant Garamond',serif; font-style:italic; font-weight:300; font-size:28px; color:rgba(145,162,176,0.86); letter-spacing:0.14em; }}
.mood {{ margin-top:285px; text-align:center; display:flex; flex-direction:column; gap:14px; }}
.mood-line {{ font-family:'Noto Serif JP',serif; font-weight:200; font-size:21px; color:rgba(138,153,166,0.72); letter-spacing:0.22em; }}
.bottom {{ position:absolute; bottom:118px; left:0; right:0; text-align:center; display:flex; flex-direction:column; align-items:center; gap:11px; }}
.acct {{ font-family:'Noto Serif JP',serif; font-weight:200; font-size:30px; color:rgba(200,210,220,0.9); letter-spacing:0.22em; }}
.bottom-rule {{ width:195px; height:1px; background:linear-gradient(to right,transparent,rgba(138,153,168,0.42),transparent); }}
.ep {{ font-family:'Cormorant Garamond',serif; font-size:17px; color:rgba(98,113,126,0.78); letter-spacing:0.2em; }}
</style></head>
<body>
<div class="bg"></div>
<div class="gradient-overlay"></div>
<div class="title-mask"></div>
<div class="content">
  <div class="top-label">{top_label}</div>
  <div class="top-rule"></div>
  <div class="title-block">
    <div class="main-title">{main_title}</div>
    <div class="mid-rule"></div>
    <div class="sub-title">{sub_title}</div>
  </div>
  <div class="mood">{mood_lines}</div>
  <div class="bottom">
    <div class="acct">静かな旅</div>
    <div class="bottom-rule"></div>
    <div class="ep">{episode}</div>
  </div>
</div>
</body></html>"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    for cfg in COVERS:
        frame_path = cfg["frame"]
        html = TEMPLATE.format(
            img=b64(frame_path),
            mime=mime(frame_path),
            bg_pos=cfg["bg_pos"],
            bg_filter=cfg.get("bg_filter", "saturate(0.80) brightness(0.60)"),
            top_label=cfg["top_label"],
            main_title=cfg["main_title"],
            sub_title=cfg["sub_title"],
            mood_lines="\n".join(f'<div class="mood-line">{l}</div>' for l in cfg["mood"]),
            episode=cfg["episode"],
        )
        out_dir = f"{OUT_DIR}/{'/'.join(cfg['key'].split('/')[:-1])}"
        os.makedirs(out_dir, exist_ok=True)
        out = f"{OUT_DIR}/{cfg['key']}.png"
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.set_content(html)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1800)
        page.screenshot(path=out, full_page=False)
        print(f"✓ {cfg['key']} → {out}")
        page.close()
    browser.close()
print("Done!")

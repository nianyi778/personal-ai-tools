#!/usr/bin/env python3
"""Generate Douyin covers for 長崎 clips."""
import base64
from playwright.sync_api import sync_playwright

OUT_DIR = "/Users/likai/Downloads/nagasaki_clips/output"

def b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

COVERS = [
    {
        "key": "nagasaki_01_highlight",
        "frame": "/Users/likai/Downloads/nagasaki_clips/output/frame_01_highlight_90.png",
        "top_label": "NAGASAKI · NIGHT WALK",
        "main_title": "長崎夜景",
        "sub_title": "Japan's Top 3 Night Views",
        "mood": ["暗闇に灯がともる", "坂を下るたびに表情が変わる", "500年の港の夜"],
        "episode": "Episode 04 · 長崎",
        "bg_pos": "center 45%",
    },
    {
        "key": "nagasaki_02_glover",
        "frame": "/Users/likai/Downloads/nagasaki_clips/output/frame_02_glover_150.png",
        "top_label": "NAGASAKI · GLOVER GARDEN",
        "main_title": "グラバー園",
        "sub_title": "Meiji Era · World Heritage",
        "mood": ["明治の洋館と石畳", "異国と日本が溶け合う場所", "ガス灯に照らされた夜"],
        "episode": "Episode 04 · 長崎",
        "bg_pos": "center 40%",
    },
    {
        "key": "nagasaki_03_slope",
        "frame": "/Users/likai/Downloads/nagasaki_clips/output/frame_03_slope_200.png",
        "top_label": "NAGASAKI · DUTCH SLOPE",
        "main_title": "坂道の夜",
        "sub_title": "Orandazaka · Kinensaká",
        "mood": ["石畳を上るたびに街が遠ざかる", "レンガ小径の先のベンチ", "誰もいない展望公園"],
        "episode": "Episode 04 · 長崎",
        "bg_pos": "center 50%",
    },
    {
        "key": "nagasaki_04_harbor",
        "frame": "/Users/likai/Downloads/nagasaki_clips/output/frame_04_harbor_15.png",
        "top_label": "NAGASAKI · HARBOR NIGHT",
        "main_title": "港の夜",
        "sub_title": "Tram · Dejima · Inasayama",
        "mood": ["路面電車が橙の夜に現れた", "出島の前を静かに通り過ぎ", "稲佐山から見た世界三大夜景"],
        "episode": "Episode 04 · 長崎",
        "bg_pos": "center 40%",
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
  background: url('data:image/png;base64,{img}') {bg_pos} / cover no-repeat;
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
        html = TEMPLATE.format(
            img=b64(cfg["frame"]),
            bg_pos=cfg["bg_pos"],
            bg_filter=cfg.get("bg_filter", "saturate(0.68) brightness(1.05)"),
            top_label=cfg["top_label"],
            main_title=cfg["main_title"],
            sub_title=cfg["sub_title"],
            mood_lines="\n".join(f'<div class="mood-line">{l}</div>' for l in cfg["mood"]),
            episode=cfg["episode"],
        )
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.set_content(html)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1800)
        out = f"{OUT_DIR}/{cfg['key']}_cover.png"
        page.screenshot(path=out, full_page=False)
        print(f"✓ {cfg['key']} → {out}")
        page.close()
    browser.close()
print("Done!")

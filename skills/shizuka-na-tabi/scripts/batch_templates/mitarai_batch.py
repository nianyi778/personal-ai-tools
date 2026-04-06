#!/usr/bin/env python3
"""批量剪辑御手洗视频，输出4条带双语字幕的成品。

章节参考：
  00:00:00 オープニング / Opening
  00:01:17 呉市豊町御手洗重要伝統的建造物群保存地区 / Mitarai Historic District
  00:05:40 町の中探索 / Exploring the Town
  00:16:41 大長 / Ochou
  00:23:36 歴史の見える丘公園 / Hill Overlooking Historic Areas
"""

import os, re, subprocess

VIDEO  = "/Users/likai/Downloads/mitarai.mp4"
OUT    = "/Users/likai/Downloads/mitarai_clips"
JA_SRT = "/tmp/sub_ja_full.srt"
ZH_SRT = "/tmp/sub_zh_full.srt"
os.makedirs(OUT, exist_ok=True)

# ── 片段规划 ───────────────────────────────────────────────
# 时间单位：秒
CLIPS = {
    "01_highlight": {
        "title": "御手洗 風待ちの港",
        "segments": [
            (6,   120),   # 灯台・石防波堤
            (198, 228),   # 天使の梯子
            (350, 410),   # 古民家路地
            (703, 750),   # 北前船の歴史 + お寺
            (1004,1035),  # 大長港
            (1329,1355),  # 防波堤の猫
            (1428,1468),  # 展望台エンディング
        ],
    },
    "02_harbor": {
        "title": "住吉神社と瀬戸内の海",
        "segments": [
            (6,   155),   # 灯台・住吉神社・石防波堤
            (198, 260),   # 天使の梯子・水辺の鳥居
            (264, 340),   # 洋風建物・朝の港
        ],
    },
    "03_machinaka": {
        "title": "江戸の息吹が残る路地",
        "segments": [
            (350, 415),   # 古民家路地・逆光
            (459, 555),   # 御手洗天満神社・郵便局・商家通り
            (620, 705),   # 天満神社 + 井戸エピソード
            (832, 900),   # 海の見える隙間・海辺の暮らし
        ],
    },
    "04_ochou": {
        "title": "大長みかんと歴史の見える丘",
        "segments": [
            (1001,1040),  # 大長港入り
            (1085,1145),  # アオサギ・生活感ある町並み
            (1270,1360),  # 海岸・防波堤・防波堤の猫
            (1416,1510),  # みかん畑・展望台・エンディング
        ],
    },
}

# ── SRT ヘルパー ───────────────────────────────────────────
def ts_to_sec(ts):
    h, m, sms = ts.split(':'); s, ms = sms.split(',')
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000

def sec_to_ts(sec):
    h = int(sec//3600); m = int((sec%3600)//60); s = int(sec%60)
    ms = round((sec - int(sec))*1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def parse_srt(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    entries = []
    for block in re.split(r'\n\s*\n', content.strip()):
        lines = block.strip().splitlines()
        if len(lines) < 3: continue
        m = re.match(r'(\S+)\s*-->\s*(\S+)', lines[1])
        if not m: continue
        entries.append({
            'start': ts_to_sec(m.group(1)),
            'end':   ts_to_sec(m.group(2)),
            'text':  '\n'.join(lines[2:]),
        })
    return entries

def make_bilingual_srt(segments, ja_entries, zh_entries, out_path):
    offsets = []; t = 0
    for s, e in segments:
        offsets.append(t - s); t += (e - s)

    def retime(entries):
        result = []
        for entry in entries:
            for i, (cs, ce) in enumerate(segments):
                if entry['end'] <= cs or entry['start'] >= ce: continue
                ns = max(entry['start'], cs) + offsets[i]
                ne = min(entry['end'],   ce) + offsets[i]
                if ne <= ns: continue
                result.append((ns, ne, entry['text']))
        return result

    ja = retime(ja_entries)
    zh_map = {}
    for e in retime(zh_entries):
        zh_map[round(e[0], 1)] = e[2]

    out = []; idx = 1
    for s, e, ja_text in ja:
        zh_text = zh_map.get(round(s, 1), '')
        text = f"{ja_text}\n{zh_text}" if zh_text else ja_text
        out.append(f"{idx}\n{sec_to_ts(s)} --> {sec_to_ts(e)}\n{text}\n")
        idx += 1

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print(f"  字幕: {idx-1} 条 → {out_path}")

# ── FFmpeg ヘルパー ────────────────────────────────────────
def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERR: {result.stderr[-300:]}")
    return result.returncode == 0

def cut_and_merge(segments, merged_path, clip_dir):
    parts = []
    for i, (s, e) in enumerate(segments):
        p = f"{clip_dir}/seg_{i:02d}.mp4"
        run(f'ffmpeg -y -ss {s} -to {e} -i "{VIDEO}" -c copy "{p}"')
        parts.append(p)
    list_path = f"{clip_dir}/list.txt"
    with open(list_path, 'w') as f:
        f.write('\n'.join(f"file '{p}'" for p in parts))
    run(f'ffmpeg -y -f concat -safe 0 -i "{list_path}" -c copy "{merged_path}"')
    return merged_path

def burn_subs(input_path, srt_path, output_path):
    import shutil, hashlib
    tmp_srt = f"/tmp/sub_{hashlib.md5(srt_path.encode()).hexdigest()[:6]}.srt"
    shutil.copy(srt_path, tmp_srt)
    style = "FontName=PingFang SC,FontSize=16,PrimaryColour=&HFFFFFF,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=40"
    cmd = (f'ffmpeg -y -i "{input_path}" '
           f'-vf "subtitles={tmp_srt}:force_style=\'{style}\'" '
           f'-c:v libx264 -crf 18 -preset fast -c:a copy "{output_path}"')
    ok = run(cmd)
    if ok: print(f"  ✓ 字幕烧录完成")

# ── Main ──────────────────────────────────────────────────
print("加载字幕文件...")
ja_entries = parse_srt(JA_SRT)
zh_entries = parse_srt(ZH_SRT)
print(f"  日文: {len(ja_entries)} 条  中文: {len(zh_entries)} 条\n")

for key, cfg in CLIPS.items():
    title    = cfg["title"]
    segments = cfg["segments"]
    clip_dir = f"{OUT}/{key}"
    os.makedirs(clip_dir, exist_ok=True)

    merged  = f"{clip_dir}/merged.mp4"
    srt_out = f"{clip_dir}/bilingual.srt"
    final   = f"/Users/likai/Downloads/mitarai_{key}_final.mp4"

    total = sum(e - s for s, e in segments)
    print(f"▶ [{key}] {title}  ({len(segments)}段, ~{total//60}分{total%60}秒)")

    print("  剪辑合并...")
    cut_and_merge(segments, merged, clip_dir)

    print("  生成双语字幕...")
    make_bilingual_srt(segments, ja_entries, zh_entries, srt_out)

    print("  烧录字幕...")
    burn_subs(merged, srt_out, final)

    size = os.path.getsize(final)/1024/1024 if os.path.exists(final) else 0
    print(f"  → {final} ({size:.0f}MB)\n")

print("🎉 全部完成！")
print("\n输出文件：")
for key in CLIPS:
    p = f"/Users/likai/Downloads/mitarai_{key}_final.mp4"
    if os.path.exists(p):
        print(f"  {p} ({os.path.getsize(p)/1024/1024:.0f}MB)")

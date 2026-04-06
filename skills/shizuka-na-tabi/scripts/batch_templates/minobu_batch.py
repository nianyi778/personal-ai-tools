"""Batch process Minobu-san Kuonji Temple video into 4 themed clips."""

import os, re, subprocess

VIDEO  = "/Users/likai/Downloads/minobu.mp4"
OUT    = "/Users/likai/Downloads/minobu_clips"
JA_SRT = "/tmp/minobu_ja.srt"
ZH_SRT = "/tmp/minobu_zh.srt"

# 输出结构：每条视频独立文件夹，内部分 封面/视频/文案
# minobu_clips/
# ├── 01_highlight/
# │   ├── 封面/         ← 取帧 + 生成封面图
# │   ├── 视频/         ← merged.mp4（取封面用）+ final.mp4（上传用）
# │   └── 文案.txt      ← 标题 + 正文 + 话题标签
# └── ...
os.makedirs(OUT, exist_ok=True)

# Segments: (start_sec, end_sec)
# Total video: ~2004s (33:24)
#
# Key chapter markers:
#  79s  = 1:19  acrobatic bell ringing
# 128s  = 2:08  Kuonji grounds (before sunrise)
# 178s  = 2:58  main gate to temple town
# 299s  = 4:59  Sanmon gate → sunrise
# 460s  = 7:40  mausoleum & hermitage
# 676s  = 11:16 Nishidani weeping cherry
# 947s  = 15:47 Kuonji grounds
# 1195s = 19:55 ropeway to Okunoin
# 1516s = 25:16 grounds (sunset)
# 1836s = 30:36 grounds (after sunset)

CLIPS = {
    "01_highlight": {
        "title": "精華版",
        # Hook: sunset 400yr cherry → bell → Sanmon sunrise → Nishidani → grounds cherry → paradise
        "segments": [
            (1582, 1617),   # 26:22-26:57  夕阳400年樱花（最强画面开场）
            (79,   115),    # 1:19-1:55    杂技式撞钟
            (299,  335),    # 4:59-5:35    三门朝阳
            (676,  755),    # 11:16-12:35  西谷垂枝樱壮观枝条
            (1037, 1082),   # 17:17-18:02  境内400年垂枝樱
            (1693, 1755),   # 28:13-29:15  "这里像极乐"
            (1836, 1863),   # 30:36-31:03  日落后大本堂
        ],
    },
    "02_sakura": {
        "title": "しだれ桜",
        # Nishidani cherry + grounds 400yr cherry
        "segments": [
            (676,  800),    # 11:16-13:20  西谷垂枝樱全段（壮观枝条+盛开）
            (870,  948),    # 14:30-15:48  西谷极乐感 + 斜坡电梯返回
            (1037, 1165),   # 17:17-19:25  境内400年樱 + 创始人堂
        ],
    },
    "03_morning": {
        "title": "夜明けの久遠寺",
        # Pre-dawn bells + morning service + main gate + Sanmon sunrise
        "segments": [
            (64,   120),    # 1:04-2:00    开场问候 + 撞钟
            (128,  250),    # 2:08-4:10    朝课开始 + 僧侣 + 总门步行
            (299,  430),    # 4:59-7:10    三门朝阳 + 菩提梯 + 境内
        ],
    },
    "04_okunoin": {
        "title": "奥之院と富士山",
        # Ropeway + ancient cedars + Mt Fuji observation
        "segments": [
            (1195, 1300),   # 19:55-21:40  索道 + 奥之院到达
            (1300, 1415),   # 21:40-23:35  700年杉树 + 礼拜 + 释迦牟尼金像
            (1415, 1516),   # 23:35-25:16  南阿尔卑斯 + 富士河 + 富士山
        ],
    },
}

# ── SRT helpers ───────────────────────────────────────────
def ts_to_sec(ts):
    h,m,sms = ts.split(':'); s,ms = sms.split(',')
    return int(h)*3600+int(m)*60+int(s)+int(ms)/1000

def sec_to_ts(sec):
    h=int(sec//3600); m=int((sec%3600)//60); s=int(sec%60)
    ms=round((sec-int(sec))*1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def parse_srt(path):
    with open(path,encoding='utf-8') as f: content=f.read()
    entries=[]
    for block in re.split(r'\n\s*\n', content.strip()):
        lines=block.strip().splitlines()
        if len(lines)<3: continue
        m=re.match(r'(\S+)\s*-->\s*(\S+)',lines[1])
        if not m: continue
        entries.append({'start':ts_to_sec(m.group(1)),'end':ts_to_sec(m.group(2)),'text':'\n'.join(lines[2:])})
    return entries

def make_bilingual_srt(segments, ja_entries, zh_entries, out_path):
    offsets=[]; t=0
    for s,e in segments:
        offsets.append(t-s); t+=(e-s)

    def retime(entries):
        result=[]
        for entry in entries:
            for i,(cs,ce) in enumerate(segments):
                if entry['end']<=cs or entry['start']>=ce: continue
                ns=max(entry['start'],cs)+offsets[i]
                ne=min(entry['end'],ce)+offsets[i]
                if ne<=ns: continue
                result.append((ns,ne,entry['text']))
        return result

    ja=retime(ja_entries)
    zh_map={}
    for e in retime(zh_entries): zh_map[round(e[0],1)]=e[2]

    out=[]; idx=1
    for s,e,ja_text in ja:
        zh_text=zh_map.get(round(s,1),'')
        text=f"{ja_text}\n{zh_text}" if zh_text else ja_text
        out.append(f"{idx}\n{sec_to_ts(s)} --> {sec_to_ts(e)}\n{text}\n")
        idx+=1

    with open(out_path,'w',encoding='utf-8') as f: f.write('\n'.join(out))
    print(f"  字幕: {idx-1} 条 → {out_path}")

# ── FFmpeg helpers ────────────────────────────────────────
def run(cmd):
    result=subprocess.run(cmd,shell=True,capture_output=True,text=True)
    if result.returncode!=0: print(f"  ERR: {result.stderr[-300:]}")
    return result.returncode==0

def cut_and_merge(segments, merged_path, clip_dir):
    parts=[]
    for i,(s,e) in enumerate(segments):
        p=f"{clip_dir}/seg_{i:02d}.mp4"
        run(f'ffmpeg -y -ss {s} -to {e} -i "{VIDEO}" -c copy "{p}"')
        parts.append(p)
    list_path=f"{clip_dir}/list.txt"
    with open(list_path,'w') as f:
        f.write('\n'.join(f"file '{p}'" for p in parts))
    run(f'ffmpeg -y -f concat -safe 0 -i "{list_path}" -c copy "{merged_path}"')
    return merged_path

def burn_subs(input_path, srt_path, output_path):
    import shutil, hashlib
    tmp_srt=f"/tmp/sub_{hashlib.md5(srt_path.encode()).hexdigest()[:6]}.srt"
    shutil.copy(srt_path, tmp_srt)
    style="FontName=PingFang SC,FontSize=16,PrimaryColour=&HFFFFFF,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=40"
    cmd=(f'ffmpeg -y -i "{input_path}" '
         f'-vf "subtitles={tmp_srt}:force_style=\'{style}\'" '
         f'-c:v libx264 -crf 18 -preset fast -c:a copy "{output_path}"')
    ok=run(cmd)
    if ok: print(f"  ✓ 字幕烧录完成")

# ── Main ─────────────────────────────────────────────────
print("加载字幕文件...")
ja_entries = parse_srt(JA_SRT)
zh_entries = parse_srt(ZH_SRT)
print(f"  日文: {len(ja_entries)} 条  中文: {len(zh_entries)} 条\n")

for key, cfg in CLIPS.items():
    title    = cfg["title"]
    segments = cfg["segments"]

    # 目录结构：封面/视频/文案 分离
    clip_dir    = f"{OUT}/{key}"
    video_dir   = f"{clip_dir}/视频"
    cover_dir   = f"{clip_dir}/封面"
    for d in [clip_dir, video_dir, cover_dir]:
        os.makedirs(d, exist_ok=True)

    total_sec = sum(e-s for s,e in segments)
    mm, ss = divmod(int(total_sec), 60)
    print(f"[{key}] {title}  时长 {mm}:{ss:02d}  ({len(segments)} 段)")

    merged  = f"{video_dir}/merged.mp4"        # 用于取封面帧
    srt_out = f"{clip_dir}/bilingual.srt"
    final   = f"{video_dir}/minobu_{key}_final.mp4"  # 上传用

    print("  切片 + 合并 → 视频/merged.mp4 ...")
    cut_and_merge(segments, merged, clip_dir)

    print("  生成双语字幕...")
    make_bilingual_srt(segments, ja_entries, zh_entries, srt_out)

    print("  烧录字幕 → 视频/final.mp4 ...")
    burn_subs(merged, srt_out, final)

    # 取 3 个候选封面帧（从 merged.mp4）
    print("  取封面帧 → 封面/ ...")
    for t in [5, 30, 60]:
        frame_path = f"{cover_dir}/frame_{t:03d}s.png"
        run(f'ffmpeg -y -ss {t} -i "{merged}" -vframes 1 "{frame_path}" 2>/dev/null')

    print(f"  → {clip_dir}/\n")

print("全部完成 ✓")
print(f"\n目录结构：{OUT}/")
print("  每条: 封面/（帧图）  视频/（merged + final）  文案.txt（待填写）")

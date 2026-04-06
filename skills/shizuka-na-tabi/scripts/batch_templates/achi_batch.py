"""Batch process Achi Village Hanamomo video into 4 themed clips."""

import os, re, subprocess

VIDEO  = "/Users/likai/Downloads/achi.mp4"
OUT    = "/Users/likai/Downloads/achi_clips"
JA_SRT = "/tmp/achi_ja.srt"
ZH_SRT = "/tmp/achi_zh.srt"

# 输出结构：每条视频独立文件夹，内部分 封面/视频/文案
# achi_clips/
# ├── 01_highlight/  封面/  视频/  文案.txt
# └── ...
os.makedirs(OUT, exist_ok=True)

# Segments: (start_sec, end_sec)
# Key timestamps:
#   38s  = 0:38  Hello / arrival
#  295s  = 4:55  back to main area
#  529s  = 8:49  walk starts, 鯉のぼり bridge appears
#  660s  = 11:00 three-color cherry walk
#  905s  = 15:05 upper river area
# 1114s  = 18:34 heading back
# 1200s  = 20:00 inn origin
# 1330s  = 22:10 原風景 / small path
# 1475s  = 24:35 heading to viewpoint
# 1519s  = 25:19 viewpoint reached
# 1619s  = 26:59 panorama / "ドイツ3本から..."

CLIPS = {
    "01_highlight": {
        "title": "精華版",
        # Hook: viewpoint panorama → arrival flowers → 満開 blue sky → 鯉のぼり → walk → close
        "segments": [
            (1519, 1550),   # 25:19-25:50  展望台HOOK（开场最强画面）
            (42,   88),     # 0:42-1:28    到达，花桃满开
            (316,  352),    # 5:16-5:52    満開 + 青空
            (529,  590),    # 8:49-9:50    鯉のぼり桥
            (660,  720),    # 11:00-12:00  三色花桃散策
            (1619, 1680),   # 26:59-28:00  展望台全景收尾
        ],
    },
    "02_story": {
        "title": "100年の物語",
        # Driving storytelling + viewpoint payoff
        "segments": [
            (38,   260),    # 0:38-4:20    开车+讲故事（桃介さん德国→日本→阿智村）
            (1475, 1530),   # 24:35-25:30  走向展望台
            (1619, 1683),   # 26:59-28:03  "ドイツ3本から…"全景结尾
        ],
    },
    "03_sanpo": {
        "title": "花桃の散策",
        # Main walking: bridge + riverside + three colors
        "segments": [
            (529,  635),    # 8:49-10:35   鯉のぼり桥 + 散策开始
            (660,  750),    # 11:00-12:30  三色花桃
            (905,  1040),   # 15:05-17:20  上游河岸
        ],
    },
    "04_miharashi": {
        "title": "展望台と原風景",
        # Inn origin + small path + viewpoint panorama
        "segments": [
            (1200, 1265),   # 20:00-21:05  旅館起源地 + 八重桜満開
            (1330, 1415),   # 22:10-23:35  原風景 小径
            (1475, 1540),   # 24:35-25:40  走向展望台
            (1580, 1683),   # 26:20-28:03  展望台全景
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

    clip_dir  = f"{OUT}/{key}"
    video_dir = f"{clip_dir}/视频"
    cover_dir = f"{clip_dir}/封面"
    for d in [clip_dir, video_dir, cover_dir]:
        os.makedirs(d, exist_ok=True)

    total_sec = sum(e-s for s,e in segments)
    mm, ss = divmod(int(total_sec), 60)
    print(f"[{key}] {title}  时长 {mm}:{ss:02d}  ({len(segments)} 段)")

    merged  = f"{video_dir}/merged.mp4"
    srt_out = f"{clip_dir}/bilingual.srt"
    final   = f"{video_dir}/achi_{key}_final.mp4"

    print("  切片 + 合并...")
    cut_and_merge(segments, merged, clip_dir)

    print("  生成双语字幕...")
    make_bilingual_srt(segments, ja_entries, zh_entries, srt_out)

    print("  烧录字幕...")
    burn_subs(merged, srt_out, final)

    print("  取封面帧...")
    for t in [5, 30, 60]:
        frame_path = f"{cover_dir}/frame_{t:03d}s.png"
        run(f'ffmpeg -y -ss {t} -i "{merged}" -vframes 1 "{frame_path}" 2>/dev/null')

    print(f"  → {clip_dir}/\n")

print("全部完成 ✓")

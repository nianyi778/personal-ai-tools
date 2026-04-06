"""Batch process Nara walking video into 4 themed clips."""

import os, re, subprocess

VIDEO  = "/Users/likai/Downloads/nara.mp4"
OUT    = "/Users/likai/Downloads/nara_clips"
JA_SRT = "/tmp/nara_ja.srt"
ZH_SRT = "/tmp/nara_zh.srt"

os.makedirs(OUT, exist_ok=True)

# Segments: (start_sec, end_sec)
# Key timestamps:
#   46s   = 0:46   奈良公園入口・鹿登場
#   80s   = 1:20   鹿の群れ・朝の光
#  160s   = 2:40   春日大社参道
#  181s   = 3:01   参道続き
#  325s   = 5:25   東大寺南大門
#  385s   = 6:25   大仏殿前
#  510s   = 8:30   大仏殿内部
#  545s   = 9:05   大仏殿続き
#  640s   = 10:40  大仏殿出口
#  760s   = 12:40  二月堂・三月堂方面
#  824s   = 13:44  二月堂からの眺め
# 1055s   = 17:35  昼・鹿と人の共存
# 1160s   = 19:20  鹿せんべい
# 1200s   = 20:00  鹿の群れ昼
# 1280s   = 21:20  夕方へ
# 1535s   = 25:35  夕暮れの奈良公園
# 1585s   = 26:25  夕陽の中の鹿
# 1625s   = 27:05  夕暮れ続き
# 1650s   = 27:30  終盤

CLIPS = {
    "01_highlight": {
        "title": "精華版",
        # Hook: 夕陽の鹿 → 朝の鹿 → 東大寺 → 大仏殿前 → 二月堂
        "segments": [
            (1585, 1625),   # 26:25-27:05  夕陽HOOK・鹿シルエット
            (80,   148),    # 1:20-2:28    朝の鹿の群れ
            (325,  385),    # 5:25-6:25    東大寺南大門
            (545,  605),    # 9:05-10:05   大仏殿内部
            (760,  820),    # 12:40-13:40  二月堂への道
        ],
    },
    "02_asa": {
        "title": "早朝の奈良",
        # 夜明けの公園 → 最初の鹿 → 参道散歩
        "segments": [
            (46,   160),    # 0:46-2:40    奈良公園入口・朝の鹿
            (181,  320),    # 3:01-5:20    春日大社参道
            (323,  398),    # 5:23-6:38    東大寺へのアプローチ
        ],
    },
    "03_todaiji": {
        "title": "東大寺",
        # 南大門 → 大仏殿 → 二月堂
        "segments": [
            (330,  510),    # 5:30-8:30    南大門〜大仏殿前
            (545,  640),    # 9:05-10:40   大仏殿内部
            (763,  824),    # 12:43-13:44  二月堂・眺め
        ],
    },
    "04_shika": {
        "title": "鹿との時間",
        # 昼の鹿 → 鹿せんべい → 夕暮れの鹿
        "segments": [
            (1055, 1160),   # 17:35-19:20  昼の鹿・人との共存
            (1200, 1280),   # 20:00-21:20  鹿せんべい・群れ
            (1535, 1650),   # 25:35-27:30  夕暮れの奈良公園・鹿シルエット
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
    if result.returncode!=0: print(f"  ERR: {result.stderr[-200:]}")
    return result.returncode==0

def cut_and_merge(segments, merged_path, clip_dir):
    parts=[]
    for i,(s,e) in enumerate(segments):
        p=f"{clip_dir}/seg_{i:02d}.mp4"
        run(f'ffmpeg -y -ss {s} -to {e} -i "{VIDEO}" -c copy "{p}" 2>/dev/null')
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
    final   = f"{video_dir}/nara_{key}_final.mp4"

    print("  切片 + 合并...")
    cut_and_merge(segments, merged, clip_dir)
    print("  生成双语字幕...")
    make_bilingual_srt(segments, ja_entries, zh_entries, srt_out)
    print("  烧录字幕...")
    burn_subs(merged, srt_out, final)
    print("  取封面帧...")
    for t in [5, 30, 60, 100, 150]:
        frame_path = f"{cover_dir}/frame_{t:03d}s.png"
        run(f'ffmpeg -y -ss {t} -i "{merged}" -vframes 1 "{frame_path}" 2>/dev/null')
    print(f"  → {clip_dir}/\n")

print("全部完成 ✓")

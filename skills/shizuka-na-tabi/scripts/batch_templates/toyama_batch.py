"""Batch process Toyama Early Summer video into 4 themed clips."""

import os, re, subprocess

VIDEO  = "/Users/likai/Downloads/toyama.mp4"
OUT    = "/Users/likai/Downloads/toyama_clips"
JA_SRT = "/tmp/toyama_ja.srt"
ZH_SRT = "/tmp/toyama_zh.srt"

os.makedirs(OUT, exist_ok=True)

# Segments: (start_sec, end_sec)
# Key timestamps:
#   40s  = 0:40  Hello Mona, Toyama
#  115s  = 1:55  雨晴駅到着
#  164s  = 2:44  海岸散歩
#  246s  = 4:06  道の駅
#  315s  = 5:15  氷見漁港出発
#  362s  = 6:02  漁港到着・魚市場
#  430s  = 7:10  秘境の寺 到着
#  497s  = 8:17  参拝・滝
#  551s  = 9:11  苔の森（隠れスポット）
#  622s  = 10:22 富山市へ
#  664s  = 11:04 富山駅・路面電車
#  705s  = 11:45 夕食タイム
#  820s  = 13:40 夜の散歩
#  900s  = 15:00 翌朝
#  921s  = 15:21 スタバ
#  980s  = 16:20 ガラス美術館
# 1190s  = 19:50 終わり

CLIPS = {
    "01_highlight": {
        "title": "精華版",
        # Hook: 苔の森 → 雨晴海岸 → 寺 → 路面電車 → 夜景
        "segments": [
            (551,  590),    # 9:11-9:50   苔の森HOOK（最も静かな画面）
            (115,  185),    # 1:55-3:05   雨晴海岸・立山眺望
            (497,  551),    # 8:17-9:11   滝行・参拝
            (664,  705),    # 11:04-11:45 富山駅路面電車
            (820,  875),    # 13:40-14:35 夜景散步
            (980,  1020),   # 16:20-17:00 ガラス美術館
        ],
    },
    "02_ameharashi": {
        "title": "雨晴海岸",
        # Morning coast + mountains + roadside station
        "segments": [
            (40,   115),    # 0:40-1:55   到着・ローカル感・富山湾
            (115,  246),    # 1:55-4:06   雨晴海岸散歩・立山
            (246,  315),    # 4:06-5:15   道の駅・カフェ
        ],
    },
    "03_temple": {
        "title": "苔の森",
        # Himi port + secret temple + waterfall + moss stream
        "segments": [
            (362,  430),    # 6:02-7:10   氷見漁港・魚市場・海鮮
            (430,  497),    # 7:10-8:17   秘境寺 到着・静寂
            (497,  622),    # 8:17-10:22  滝行・苔の森・渓流
        ],
    },
    "04_toyama": {
        "title": "夜の富山とガラス",
        # Night walk + morning Starbucks + glass museum
        "segments": [
            (820,  900),    # 13:40-15:00 夜の散歩・夜景
            (900,  980),    # 15:00-16:20 翌朝・スタバ・緑
            (980,  1185),   # 16:20-19:45 ガラス美術館
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
print("加载字幕...")
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
    final   = f"{video_dir}/toyama_{key}_final.mp4"

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

#!/usr/bin/env python3
"""Batch process 天ヶ瀬温泉 video into 4 themed clips with bilingual subtitles."""

import os, re, subprocess

VIDEO  = "/Users/likai/Downloads/amagase.mp4"
OUT    = "/Users/likai/Downloads/amagase_clips"
JA_SRT = "/tmp/amagase_ja.srt"
ZH_SRT = "/tmp/amagase_zh.srt"
os.makedirs(OUT, exist_ok=True)

CLIPS = {
    "01_highlight": {
        "title": "大分・天ヶ瀬温泉",
        "segments": [(4,25),(1192,1255),(1384,1440),(1530,1580),(1944,2010),(2879,2945)],
    },
    "02_onsen_town": {
        "title": "天ヶ瀬温泉街",
        "segments": [(813,858),(870,930),(1060,1125),(1192,1260),(1384,1445)],
    },
    "03_ryokan": {
        "title": "山荘天水",
        "segments": [(1535,1590),(1765,1830),(1944,2010),(2360,2425),(2664,2725)],
    },
    "04_dinner": {
        "title": "夕食と湯",
        "segments": [(2815,2875),(2895,2960),(3145,3210),(3258,3330),(3405,3445)],
    },
}

# ── SRT helpers ──────────────────────────────────────────────
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
        m=re.match(r'(\S+)\s*-->\\s*(\S+)',lines[1])
        if not m: m=re.match(r'(\S+)\s*-->\s*(\S+)',lines[1])
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

# ── FFmpeg helpers ────────────────────────────────────────────
def run(cmd):
    result=subprocess.run(cmd,shell=True,capture_output=True,text=True)
    if result.returncode!=0: print(f"  ERR: {result.stderr[-300:]}")
    return result.returncode==0

def cut_and_merge(segments, merged_path, clip_dir):
    parts=[]
    for i,(s,e) in enumerate(segments):
        p=f"{clip_dir}/seg_{i:02d}.mp4"
        dur=e-s
        # AV1 source: re-encode to H.264 for accurate frame-level cuts
        run(f'ffmpeg -y -ss {s} -t {dur} -i "{VIDEO}" '
            f'-c:v libx264 -crf 20 -preset ultrafast -c:a aac -b:a 192k "{p}"')
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

# ── Main ──────────────────────────────────────────────────────
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
    final   = f"/Users/likai/Downloads/amagase_{key}_final.mp4"

    total = sum(e-s for s,e in segments)
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
for key in CLIPS:
    p = f"/Users/likai/Downloads/amagase_{key}_final.mp4"
    if os.path.exists(p):
        print(f"  {p} ({os.path.getsize(p)/1024/1024:.0f}MB)")

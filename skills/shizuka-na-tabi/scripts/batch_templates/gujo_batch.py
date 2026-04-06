"""Batch process Gujo Hachiman Summer video into 4 themed clips."""

import os, re, subprocess

VIDEO  = "/Users/likai/Downloads/gujo.mp4"
OUT    = "/Users/likai/Downloads/gujo_clips"
JA_SRT = "/tmp/gujo_ja.srt"
ZH_SRT = "/tmp/gujo_zh.srt"

os.makedirs(OUT, exist_ok=True)

# Segments: (start_sec, end_sec)
# Key timestamps:
#   44s  = 0:44  Hello Mona, 岐阜県
#  107s  = 1:47  寄り道・妖怪神社
#  270s  = 4:30  神社終わり
#  282s  = 4:42  郡上八幡駅到着
#  391s  = 6:31  ランチ（吉田川沿い）
#  513s  = 8:33  散策・吉田川青緑
#  682s  = 11:22 暑い → 天然水サイダー
#  777s  = 12:57 古民家カフェ・抹茶スイーツ
#  870s  = 14:30 夕方・子ども水遊び
#  900s  = 15:00 名水百選
# 1005s  = 16:45 郡上八幡城
# 1140s  = 19:00 ホテル
# 1194s  = 19:54 郡上おどり
# 1284s  = 21:24 おどり終わり
# 1294s  = 21:34 翌朝散歩
# 1437s  = 23:57 天ぷらうどん
# 1518s  = 25:18 鍾乳洞・木製ケーブルカー
# 1682s  = 28:02 終わり

CLIPS = {
    "01_highlight": {
        "title": "精華版",
        # Hook: 地底大滝 → 神社虹 → 郡上おどり → 吉田川 → 城の眺め
        "segments": [
            (1620, 1660),   # 27:00-27:40  地底大滝HOOK
            (127,  200),    # 2:07-3:20    妖怪神社・杉・虹の隠れスポット
            (1194, 1250),   # 19:54-20:50  郡上おどり熱気
            (540,  605),    # 9:00-10:05   吉田川の青緑
            (1005, 1065),   # 16:45-17:45  城から一望
        ],
    },
    "02_mizu": {
        "title": "水の町",
        # 駅 → 商店街 → 用水路 → 吉田川 → 名水 → 朝の鯉
        "segments": [
            (300,  395),    # 5:00-6:35    郡上八幡駅・商店街・用水路鯉
            (513,  610),    # 8:33-10:10   吉田川の青緑 + 民家裏用水路
            (900,  950),    # 15:00-15:50  名水百選・子ども水遊び
            (1294, 1370),   # 21:34-22:50  翌朝散歩・鯉に餌やり
        ],
    },
    "03_shizen": {
        "title": "神社と鍾乳洞",
        # 妖怪神社・虹 → 木製ケーブルカー → 鍾乳洞 → 地底大滝
        "segments": [
            (107,  270),    # 1:47-4:30    妖怪神社・杉の巨木・虹の隠れスポット
            (1518, 1682),   # 25:18-28:02  木製ケーブルカー→鍾乳洞→地底大滝
        ],
    },
    "04_odori": {
        "title": "城と夏祭り",
        # 郡上八幡城 → 郡上おどり（夜）→ 天ぷらうどん
        "segments": [
            (1005, 1125),   # 16:45-18:45  郡上八幡城・最上階の眺め
            (1194, 1290),   # 19:54-21:30  郡上おどり（夜）
            (1440, 1520),   # 24:00-25:20  天ぷらうどん
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
    # Compute output offsets
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
    # Copy srt to /tmp for ffmpeg (no special chars in path)
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
    final   = f"{video_dir}/gujo_{key}_final.mp4"

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

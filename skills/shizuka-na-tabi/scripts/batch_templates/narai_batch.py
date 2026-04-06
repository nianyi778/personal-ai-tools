"""Batch process Narai-juku / Toriitouge / Yabuhara walking video into 3 themed clips."""

import os, re, subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed

# ── 第一人称视角过滤 ────────────────────────────────────────
# 抹掉原 YouTuber 的自我介绍、频道推广、结尾语等三方痕迹
BLOCK_PATTERNS = [
    r'みなさん(こんにちは|こんばんは)',
    r'(チャンネル登録|チャンネル読者)',
    r'ご視聴ありがとう',
    r'また次の動画で',
    r'バイバイ',
    r'今回は.{0,20}(にやってきました|を訪れ)',
    r'(わたたび|たびこ|旅系YouTuber)',
]

def filter_entries(entries):
    return [e for e in entries if not any(re.search(p, e['text']) for p in BLOCK_PATTERNS)]

VIDEO  = "/Users/likai/Downloads/narai.mp4"
OUT    = "/Users/likai/Downloads/narai_clips"
JA_SRT = "/tmp/narai_ja.srt"
ZH_SRT = "/tmp/narai_zh.srt"

os.makedirs(OUT, exist_ok=True)

# Key timestamps:
#   0:45   = 0:45   到着・奈良井川の橋
#   1:20   = 1:20   川沿い歩き
#   3:23   = 3:23   奈良井宿 入口
#   7:30   = 7:30   灯篭・もみじ・中央付近
#   9:21   = 9:21   水場の音
#  11:24   = 11:24  山頂から太陽が顔を出す
#  13:53   = 13:53  真っ赤な紅葉（クリムゾンレッド）
#  15:30   = 15:30  山道急坂・落ち葉
#  20:33   = 20:33  逆光のもみじ
#  20:49   = 20:49  東屋・藪原宿の絶景パノラマ
#  27:48   = 27:48  藪原宿 到着
#  28:08   = 28:08  「まるでふるさとに戻ってきたような感覚」
#  30:30   = 30:30  人の気配なし・全てを独り占め

CLIPS = {
    "01_highlight": {
        "title": "精华版",
        # Hook: 東屋からの藪原宿絶景 → 橋・川・夜明け前 → 朝日 → 真紅紅葉 → 藪原宿
        "segments": [
            (1249, 1302),  # 20:49-21:42  東屋+藪原宿絶景 HOOK
            (45,   100),   # 0:45-1:40    橋・川・夜明け前
            (684,  737),   # 11:24-12:17  太陽が山頂から顔を出す
            (833,  893),   # 13:53-14:53  真っ赤な紅葉
            (1688, 1735),  # 28:08-28:55  藪原宿
        ],
    },
    "02_shuku": {
        "title": "奈良井宿・夜明け",
        # Hook: 川沿い → 古い町並み → 灯篭・もみじ → 水場
        "segments": [
            (80,   138),   # 1:20-2:18    川沿い・橋
            (219,  310),   # 3:39-5:10    古い町並み
            (450,  519),   # 7:30-8:39    灯篭・もみじ
            (561,  596),   # 9:21-9:56    水場の音
        ],
    },
    "03_yama": {
        "title": "鳥居峠・藪原宿",
        # Hook: 真紅紅葉 → 山道急坂 → 東屋絶景 → 藪原宿
        "segments": [
            (833,  893),   # 13:53-14:53  真っ赤な紅葉 HOOK
            (930,  1000),  # 15:30-16:40  山道急坂・落ち葉
            (1249, 1302),  # 20:49-21:42  東屋+藪原宿絶景
            (1680, 1737),  # 28:00-28:57  藪原宿
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
    print(f"  [{out_path.split('/')[-3]}] 字幕: {idx-1} 条")

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
    if ok: print(f"  [{output_path.split('/')[-3]}] ✓ 字幕烧录完成", flush=True)

# ── Per-clip worker ───────────────────────────────────────
def process_clip(args):
    key, cfg, ja_entries, zh_entries = args
    title    = cfg["title"]
    segments = cfg["segments"]
    clip_dir  = f"{OUT}/{key}"
    video_dir = f"{clip_dir}/视频"
    cover_dir = f"{clip_dir}/封面"
    for d in [clip_dir, video_dir, cover_dir]:
        os.makedirs(d, exist_ok=True)

    total_sec = sum(e-s for s,e in segments)
    mm, ss = divmod(int(total_sec), 60)
    print(f"[{key}] {title}  时长 {mm}:{ss:02d}  ({len(segments)} 段)", flush=True)

    merged  = f"{video_dir}/merged.mp4"
    srt_out = f"{clip_dir}/bilingual.srt"
    final   = f"{video_dir}/narai_{key}_final.mp4"

    cut_and_merge(segments, merged, clip_dir)
    make_bilingual_srt(segments, ja_entries, zh_entries, srt_out)
    burn_subs(merged, srt_out, final)

    for t in [5, 30, 60, 100, 150]:
        frame_path = f"{cover_dir}/frame_{t:03d}s.png"
        run(f'ffmpeg -y -ss {t} -i "{merged}" -vframes 1 "{frame_path}" 2>/dev/null')
    print(f"  [{key}] ✓ → {clip_dir}/\n", flush=True)
    return key

# ── Main ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("加载字幕文件...")
    ja_entries = filter_entries(parse_srt(JA_SRT))
    zh_entries = parse_srt(ZH_SRT)
    print(f"  日文: {len(ja_entries)} 条  中文: {len(zh_entries)} 条\n")

    tasks = [(key, cfg, ja_entries, zh_entries) for key, cfg in CLIPS.items()]
    print(f"并行处理 {len(tasks)} 条（{len(tasks)} 进程）...\n")

    with ProcessPoolExecutor(max_workers=len(tasks)) as ex:
        futs = {ex.submit(process_clip, t): t[0] for t in tasks}
        for f in as_completed(futs):
            key = futs[f]
            try:
                f.result()
            except Exception as e:
                print(f"  ✗ [{key}] 出错: {e}")

    print("全部完成 ✓")

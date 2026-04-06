# 静かな旅 · 视频发布 SOP

> 适用平台：抖音
> 内容类型：沉浸式城市漫步（日本 / 欧美唯美风格）

---

## 依赖工具 & Skills

| 工具 | 用途 | 安装 |
|------|------|------|
| `yt-dlp` | 下载 YouTube 4K 视频 | `brew install yt-dlp` |
| `ffmpeg`（with libass） | 视频剪辑 / 字幕烧录 | `brew tap homebrew-ffmpeg/ffmpeg && brew install homebrew-ffmpeg/ffmpeg/ffmpeg --with-libass` |
| `baoyu-youtube-transcript` skill | 下载 SRT 字幕（日文/中文） | `npx skills add baoyu/skills@baoyu-youtube-transcript` |
| Playwright（Python） | 封面图渲染（HTML→PNG） | `pip install playwright && python3 -m playwright install chromium` |

**项目脚本**（均在 `~/Downloads/静かな旅/`）：

| 脚本 | 用途 |
|------|------|
| `gujo_batch.py` | 郡上八幡批量剪辑模板 |
| `kanazawa_batch.py` | 金沢批量剪辑模板（新视频改路径复用） |
| `make_covers.py` | 封面图生成（修改 COVERS 列表即可） |
| `douyin_publish.py` | 抖音半自动发布（扫码登录） |

---

## 账号风格标准（每期必须遵守）

**视觉风格：**
- 画质：4K 60fps 优先，低饱和、冷色调、电影感
- 字幕：日文（上）+ 中文（下），白色描边，无黑底，PingFang SC 16px
- 封面：1080×1920，深色渐变叠加，Noto Serif JP 极细体，主标题日文2-4字

**内容风格：**
- 题材：古街、雨天、雪景、庭园、水边等唯美场景
- 节奏：沉浸慢节奏，不加BGM替换，保留原声
- 时长：4:30～5:30（抖音完播率最佳区间）

**文案风格：**
- 语言：标题 + 正文一律**日文**
- 结构：钩子句（1行）→ 场景描写（2-3行短句）→ 情感收尾（1行）
- 固定结尾：`🎧 イヤホン推奨`
- 标签：最多5个（抖音限制）

---

## STEP 1 · 素材筛选

**来源标准：**
- YouTube 上的城市 walk-around 类视频
- 画质 4K 60fps 优先
- 内容：古街、雪景、雨天、庭园、水边等唯美场景
- 有人工制作字幕（多语言）优先

**参考频道：**
- Aoi Travel Video（已用）
- 同类型频道持续收集

---

## STEP 2 · 下载原视频

```bash
# 查看可用画质
yt-dlp -F '<YouTube URL>'

# 下载 4K（格式 401=4K视频 + 140=音频）
yt-dlp -f "401+140" --merge-output-format mp4 \
  -o "~/Downloads/<地名>.mp4" '<YouTube URL>'
```

---

## STEP 3 · 获取双语字幕

```bash
# 查看可用字幕语言
bun ~/.claude/skills/baoyu-youtube-transcript/scripts/main.ts '<URL>' --list

# 下载日文字幕（SRT格式）
bun ~/.claude/skills/baoyu-youtube-transcript/scripts/main.ts '<URL>' \
  --languages ja --format srt --refresh -o /tmp/sub_ja_full.srt

# 下载中文字幕（SRT格式）
bun ~/.claude/skills/baoyu-youtube-transcript/scripts/main.ts '<URL>' \
  --languages zh-Hans --format srt -o /tmp/sub_zh_full.srt
```

---

## STEP 4 · 规划剪辑片段

**分集策略：**
- 先通读字幕，识别视频中的地点/主题分区
- **第一条出综合精华**（时长 5min，覆盖所有地点亮点）
- 再按地点或主题拆 2～4 条，每条各有侧重，内容不重叠
- 每条目标时长：4:30～5:30，选 4～7 个片段，每段 20～70 秒
- 开头 15 秒必须有强吸引力画面

**片段记录格式（填入 batch 脚本的 CLIPS 字典）：**

```python
CLIPS = {
    "01_highlight": {"title": "综合精华", "segments": [(s1,e1),(s2,e2),...]},
    "02_theme_a":   {"title": "主题名",   "segments": [(s1,e1),...]},
    # ...
}
```

---

## STEP 5 & 6 · 剪辑 + 字幕（批量一键完成）

复制 `kanazawa_batch.py`，修改顶部三个变量后运行：

```python
VIDEO  = "/Users/likai/Downloads/<地名>.mp4"   # 原片路径
JA_SRT = "/tmp/sub_ja_full.srt"                # 日文字幕
ZH_SRT = "/tmp/sub_zh_full.srt"                # 中文字幕
```

脚本自动完成：切片 → concat 合并 → 双语字幕对齐 → 烧录 → 输出 `<地名>_<key>_final.mp4`

---

## STEP 7 · 制作视频封面

**取帧（必须从 merged.mp4，不可用 _final.mp4）：**

> ⚠️ `_final.mp4` 已烧录字幕，取帧会有字幕污染封面。

```bash
# 多取几个时间点，选最美的帧
for t in 20 60 100 150; do
  ffmpeg -y -ss $t -i "~/Downloads/<地名>_clips/<key>/merged.mp4" \
    -vframes 1 /tmp/frame_${t}.png 2>/dev/null
done
```

**生成封面：**
修改 `make_covers.py` 顶部的 `COVERS` 列表，填入选好的帧路径和文字，运行即可：

```bash
python3 ~/Downloads/静かな旅/make_covers.py
```

---

## STEP 8 · 撰写发布文案

> ⚠️ 标题和正文一律使用**日文**，体现账号调性。

**抖音（日文）：**

> ⚠️ 抖音话题标签**最多5个**，超出无效。

```
[タイトル：1行，地名＋情绪，制造代入感]

[场景描写2〜3句，短句，有画面感]

[情感收尾1句]

🎧 イヤホン推奨
#地名 #日本旅行 #まち歩き #癒し系 #没入旅行
```

---

## STEP 9 · 发布检查清单

- [ ] 视频时长 4:30 ～ 5:30
- [ ] 字幕正确显示（日文上 / 中文下）
- [ ] 封面图已准备（1080×1920）
- [ ] 标题日文，含地名关键词
- [ ] 话题标签恰好5个
- [ ] 发布后登记到 `静かな旅_発布記録.md`
- [ ] 抖音：晚上 8～10 点发布

---

## 文件命名规范

```
~/Downloads/
├── <地名>.mp4                          # 原片（4K，处理完删除）
├── <地名>_clips/                       # 中间文件（处理完删除）
│   ├── <key>/merged.mp4               # 合并后无字幕版（取封面帧用）
│   ├── <key>/bilingual.srt
│   └── <key>/seg_xx.mp4
├── <地名>_<key>_final.mp4             # 含字幕成品（上传后删除）
└── 静かな旅/                           # 项目资源（永久保留）
    ├── 静かな旅_SOP.md
    ├── 静かな旅_発布記録.md
    ├── kanazawa_batch.py              # 剪辑模板
    ├── make_covers.py                 # 封面模板
    └── douyin_publish.py              # 发布脚本
```

---

*最后更新：2026-03-22*

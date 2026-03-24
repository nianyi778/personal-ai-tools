---
name: shizuka-na-tabi
description: Use when working on the 静かな旅 Douyin account — starting a new video, processing clips, making covers, writing copy, or publishing. Load at the start of every session involving this account.
---

# 静かな旅 · 工作流

## 账号铁律（每次都必须遵守）

| 规则 | 说明 |
|------|------|
| 标题 / 正文 | 一律**日文** |
| 抖音话题标签 | **最多 5 个** |
| 封面取帧 | 必须从 `merged.mp4`，**绝对不能**用 `_final.mp4`（已烧字幕） |
| 封面文字 | 生成后目视确认所有文字清晰可读；标题区背景过亮则换帧或调暗中央渐变 |
| 字幕样式 | 日文（上）+ 中文（下），PingFang SC 16px，白色描边，无黑底 |
| 视频时长 | 4:30 ～ 5:30 |
| 发布前 | 查 発布記録.md，避免重复发布同一素材 |

## 项目目录结构

```
~/Downloads/静かな旅/
├── 静かな旅_SOP.md          # 详细操作说明
├── 静かな旅_発布記録.md      # 发布记录（每次发布后更新）
├── make_covers.py            # 封面生成脚本
├── douyin_publish.py         # 抖音半自动发布脚本
├── kanazawa_batch.py         # 金沢剪辑模板（新视频改路径复用）
└── takayama_batch.py         # 飛騨高山剪辑模板
```

## 完整流程（新视频）

### STEP 1 · 查重 + 素材确认
```bash
# 先看发布记录，确认素材未发布过
cat ~/Downloads/静かな旅/静かな旅_発布記録.md
```

### STEP 2 · 下载视频
```bash
yt-dlp -F '<URL>'   # 查看画质
yt-dlp -f "401+140" --merge-output-format mp4 \
  -o "~/Downloads/<地名>.mp4" '<URL>'
```

### STEP 3 · 下载双语字幕
```bash
# 日文（加 --refresh 避免缓存返回错误字幕）
bun ~/.claude/skills/baoyu-youtube-transcript/scripts/main.ts '<URL>' \
  --languages ja --format srt --refresh -o /tmp/<地名>_ja.srt

# 中文
bun ~/.claude/skills/baoyu-youtube-transcript/scripts/main.ts '<URL>' \
  --languages zh-Hans --format srt -o /tmp/<地名>_zh.srt
```

### STEP 4 · 规划分集
- 通读字幕，识别地点 / 主题分区
- **第一条出综合精华**（5min，覆盖所有亮点）
- 再拆 2～4 条主题条，内容不重叠
- 每条 4:30～5:30，选 4～7 个片段，每段 20～70 秒
- 开头 15 秒必须有强吸引力画面

### STEP 5 · 剪辑（批量脚本）
复制 `kanazawa_batch.py`，修改顶部三个变量后运行：
```python
VIDEO  = "/Users/likai/Downloads/<地名>.mp4"
JA_SRT = "/tmp/<地名>_ja.srt"
ZH_SRT = "/tmp/<地名>_zh.srt"
```
脚本自动完成：切片 → concat → 双语字幕对齐 → 烧录 → 输出 `<地名>_<key>_final.mp4`

### STEP 6 · 制作封面

#### 6a · 取帧
```bash
# 从 merged.mp4 取帧（多取几个，选最美的）
for t in 20 60 100 150; do
  ffmpeg -y -ss $t -i "~/Downloads/<地名>_clips/<key>/merged.mp4" \
    -vframes 1 /tmp/frame_${t}.png 2>/dev/null
done
```

#### 6b · 选帧标准（文字可读性优先）
优先选**标题区（画面中央 40-60% 高度）自然偏暗**的帧：

| 好帧 ✓ | 差帧 ✗ |
|--------|--------|
| 瀑布、水面、树荫、夜景 | 天空、电线杆、白墙建筑 |
| 画面中央有阴影或景深虚化 | 中央有高亮反光或杂乱元素 |
| 色调整体偏冷/深 | 大面积浅灰、米白、雪景 |

**如果找不到好帧**，在 cover config 里单独加 `bg_filter` 压暗原图：
```python
"bg_filter": "saturate(0.55) brightness(0.65)",  # 亮帧专用
```

**重要**：`bg_filter` 只作用于 `.bg` 背景层，与文字层完全隔离（文字在 z-index:20，背景在 z-index:0），filter 不会压暗文字。层级结构：
```
body
 ├── .bg               z-index:0  ← filter 在这里，只压背景
 ├── .gradient-overlay z-index:2  ← 上下渐变遮罩
 ├── .title-mask       z-index:5  ← 标题区椭圆暗化
 └── .content          z-index:20 ← 所有文字，不受 filter 影响
```

#### 6c · 生成 & 验证
```bash
# 修改 make_covers.py 顶部 COVERS 列表，填入帧路径和文字
python3 ~/Downloads/静かな旅/make_covers.py
```

**生成后必须目视检查**：日文主标题、英文副标题、三行 mood 文字是否全部清晰可读。若任意文字与背景对比不足，回到 6b 换帧或调参，重新生成。

### STEP 7 · 撰写文案（日文）

生成每条视频的文案后，**立即写入 txt 文件**，路径：
`~/Downloads/静かな旅/<地名>_copy.txt`

文件格式（每条用 `---` 分隔）：
```
=== 01_highlight ===
タイトル：xxx

场景描写句1
场景描写句2
情感收尾句

🎧 イヤホン推奨
#地名 #日本旅行 #まち歩き #癒し系 #没入旅行

---
=== 02_xxx ===
...
```

写完后告知用户文件路径，方便直接打开复制。

### STEP 8 · 发布 & 收尾
- [ ] 视频时长 4:30 ～ 5:30 ✓
- [ ] 封面已准备（1080×1920）✓
- [ ] 标题日文，含地名关键词 ✓
- [ ] 话题标签恰好 5 个 ✓
- [ ] 抖音晚上 8～10 点发布
- [ ] 更新 `静かな旅_発布記録.md`
- [ ] 删除原片 + 中间文件（上传后）

## 已发布素材

**不在此处维护** — 始终以文件为准：

```bash
cat ~/Downloads/静かな旅/静かな旅_発布記録.md
```

每次开始新视频前必须读取，确认素材未重复发布。

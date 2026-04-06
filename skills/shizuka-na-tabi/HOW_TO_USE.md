# 静かな旅 · 使用说明

## 你只需要做两件事

1. **上传视频到抖音**（每条视频我会给你文件路径 + 文案）
2. **定期把运营数据截图/表格丢给我**（发布后3天看一次）

其他所有事情（搜素材→下载→剪辑→封面→文案→排期）都由 Claude 完成。

---

## 每次新会话怎么开始

打开 Claude Code，直接说：
- **给数据**：「这是本周数据 [粘贴数据]」
- **要下一条**：「开始下一条视频」
- **看计划**：「现在 pipeline 是什么状态」

Claude 会自动加载 `shizuka-na-tabi` skill，读取 pipeline.md 和発布記録，决定下一步。

---

## 文件在哪里取

每次制作完成，Claude 会告诉你：

```
📁 ~/Downloads/静かな旅_work/📦发布包/<地名>/
   01_highlight_final.mp4   ← 上传抖音（选这个文件）
   cover_01_highlight.png   ← 封面（上传时选封面）
   copy.txt                 ← 文案（复制粘贴标题+正文+tag）
```

---

## 工程目录结构

```
~/personage/静かな旅/          ← 工程根（git 管理）
├── SKILL.md                  ← Claude 账号 SOP（自动加载）
├── pipeline.md               ← 内容流水线（待制作/待发布队列）
├── 静かな旅_発布記録.md       ← 已发布完整记录
├── scripts/
│   ├── config.py             ← 路径配置（不要改）
│   ├── make_covers.py        ← 封面生成器
│   └── batch_templates/     ← 历史批处理脚本存档
└── HOW_TO_USE.md             ← 本文件

~/Downloads/静かな旅_work/     ← 工作目录（大文件，不进 git）
├── 📦发布包/                 ← 成品取件处
│   └── <地名>/
│       ├── *_final.mp4
│       ├── cover_*.png
│       └── copy.txt
└── <地名>_clips/             ← 中间产物（发布后可删）
```

---

## 发布后记得

发布后告诉 Claude「已发布」，我会更新 発布記録.md 并 git push。

---

## 数据反馈格式（发布后3天）

直接把抖音后台截图丢给我即可，或者粘贴文字版：

```
视频：[标题]
播放量：xxx  点赞：xx  收藏：xx  分享：xx
2s跳出率：xx%  5s完播率：xx%  平均时长：xxs
粉丝增量：+xx
```

---

## GitHub 仓库

`https://github.com/nianyi778/shizuka-na-tabi`（private）

每次 Claude 更新了 SKILL.md / pipeline.md / 発布記録.md，会自动 commit + push。

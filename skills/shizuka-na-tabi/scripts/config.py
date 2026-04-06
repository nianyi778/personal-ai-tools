"""
静かな旅 · 路径配置

所有脚本通过 from config import * 获取路径，不再硬编码 /Users/likai。
"""

from pathlib import Path

# ── 根目录 ──────────────────────────────────────────────────
# 工程根：~/personage/shizuka-na-tabi
PROJECT_ROOT = Path(__file__).parent.parent

# ── 工作目录（大文件，不进 git，gitignored）─────────────────
# 原片、clips、发布包均放工程根目录，统一管理
WORK_DIR = PROJECT_ROOT
WORK_DIR.mkdir(parents=True, exist_ok=True)

# ── 子目录 ──────────────────────────────────────────────────
SCRIPTS_DIR      = PROJECT_ROOT / "scripts"
TRANSCRIPTS_DIR  = PROJECT_ROOT / "transcripts"
PUBLISH_PKG_DIR  = WORK_DIR / "📦発布包"
PUBLISH_PKG_DIR.mkdir(parents=True, exist_ok=True)

# ── 字幕工具 ────────────────────────────────────────────────
TRANSCRIPT_SCRIPT = (
    Path.home() / ".claude" / "skills" /
    "baoyu-youtube-transcript" / "scripts" / "main.ts"
)

# ── 常用路径生成函数 ─────────────────────────────────────────
def video_path(name: str) -> Path:
    """原片路径：~/Downloads/静かな旅_work/<name>.mp4"""
    return WORK_DIR / f"{name}.mp4"

def clips_dir(name: str) -> Path:
    """clips 输出目录"""
    d = WORK_DIR / f"{name}_clips"
    d.mkdir(parents=True, exist_ok=True)
    return d

def pkg_dir(name: str) -> Path:
    """发布包目录：包含 final.mp4 / cover.png / copy.txt"""
    d = PUBLISH_PKG_DIR / name
    d.mkdir(parents=True, exist_ok=True)
    return d

def srt_path(name: str, lang: str) -> Path:
    """字幕临时文件"""
    return Path("/tmp") / f"{name}_{lang}.srt"

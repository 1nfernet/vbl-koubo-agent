"""
前置多源摄取器 (Ingest Pipe)
负责将外部视频链接 (YouTube / B站 / TikTok) 抽取字幕或音频
具备降级保护：在未安装 yt-dlp 环境下给出友好引导，绝不导致核心程序崩溃
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from vbl_koubo.distiller.cleaner import clean_corpus_text


def check_ytdlp_available() -> bool:
    """检查系统环境是否包含 yt-dlp 可执行文件"""
    return shutil.which("yt-dlp") is not None


def ingest_from_url(
    url: str,
    blogger_name: str,
    base_corpus_dir: Optional[Path] = None
) -> Tuple[bool, str]:
    """
    通过链接摄取字幕到 corpus/<blogger>/raw/ 并清洗到 corpus/<blogger>/cleaned/
    返回: (成功状态, 结果消息或清洗后的文件路径)
    """
    if base_corpus_dir is None:
        base_corpus_dir = Path(__file__).resolve().parent.parent.parent / "corpus"

    raw_dir = base_corpus_dir / blogger_name / "raw"
    cleaned_dir = base_corpus_dir / blogger_name / "cleaned"
    raw_dir.mkdir(parents=True, exist_ok=True)
    cleaned_dir.mkdir(parents=True, exist_ok=True)

    if not check_ytdlp_available():
        return False, (
            "⚠️ 当前系统未检测到 yt-dlp 命令行工具。\n"
            "建议通过 `brew install yt-dlp` 安装，或直接将文案粘贴至:\n"
            f"   {raw_dir}/sample1.txt"
        )

    # 优先使用 yt-dlp 抽取字幕（--skip-download 不下载视频，极速模式）
    output_template = str(raw_dir / "%(id)s.%(ext)s")
    cmd = [
        "yt-dlp",
        "--write-sub",
        "--write-auto-sub",
        "--sub-lang", "zh.*,en.*",
        "--skip-download",
        "-o", output_template,
        url
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        if proc.returncode != 0:
            # 尝试最基础下载
            return False, f"yt-dlp 提取字幕失败，请检查视频链接或网络: {proc.stderr[:200]}"
    except Exception as e:
        return False, f"执行 yt-dlp 异常: {str(e)}"

    # 扫描 raw_dir 中刚生成的字幕文件 (.vtt, .srt)
    sub_files = list(raw_dir.glob("*.vtt")) + list(raw_dir.glob("*.srt"))
    if not sub_files:
        return False, "视频处理成功，但该视频未提供官方或自动生成的软字幕。"

    latest_sub = sorted(sub_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]
    raw_text = latest_sub.read_text(encoding="utf-8", errors="ignore")
    cleaned_text = clean_corpus_text(raw_text)

    # 写入 cleaned 目录
    cleaned_file = cleaned_dir / f"{latest_sub.stem}.txt"
    cleaned_file.write_text(cleaned_text, encoding="utf-8")

    return True, str(cleaned_file)


def ingest_from_text(
    text_content: str,
    blogger_name: str,
    sample_name: str = "sample1",
    base_corpus_dir: Optional[Path] = None
) -> str:
    """
    手动提供文本语料时的入库流程（写入 raw/ 并清洗至 cleaned/）
    """
    if base_corpus_dir is None:
        base_corpus_dir = Path(__file__).resolve().parent.parent.parent / "corpus"

    raw_dir = base_corpus_dir / blogger_name / "raw"
    cleaned_dir = base_corpus_dir / blogger_name / "cleaned"
    raw_dir.mkdir(parents=True, exist_ok=True)
    cleaned_dir.mkdir(parents=True, exist_ok=True)

    raw_file = raw_dir / f"{sample_name}.txt"
    raw_file.write_text(text_content, encoding="utf-8")

    cleaned_text = clean_corpus_text(text_content)
    cleaned_file = cleaned_dir / f"{sample_name}.txt"
    cleaned_file.write_text(cleaned_text, encoding="utf-8")

    return str(cleaned_file)

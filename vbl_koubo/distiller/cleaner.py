"""
语料清洗器 (Corpus Cleaner)
负责将 raw 语料（SRT 格式、VTT 格式或原始口语草稿）清洗为标准的自然段落逐字稿
存入 corpus/<blogger>/cleaned/
"""

import re
from typing import List


def strip_srt_timestamps(srt_text: str) -> str:
    """
    剥离 SRT 字幕序号与时间戳
    例如：
    1
    00:00:01,000 --> 00:00:03,500
    这里是VBL。
    """
    lines = srt_text.splitlines()
    clean_lines = []
    
    timestamp_pattern = re.compile(r'^\d{2}:\d{2}:\d{2}[,\.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,\.]\d{3}')
    index_pattern = re.compile(r'^\d+$')

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        if index_pattern.match(line_str):
            continue
        if timestamp_pattern.match(line_str):
            continue
        if line_str.startswith("WEBVTT") or line_str.startswith("NOTE"):
            continue
        clean_lines.append(line_str)

    # 合并为自然段落
    return " ".join(clean_lines)


def remove_spoken_fillers(text: str) -> str:
    """
    清洗明显的口癖词（如反复出现的“呃”、“啊”、“那个那个”）
    """
    fillers = [r'\b呃\b', r'\b啊\b', r'\b嗯\b', r'那个那个', r'就是说啊']
    for p in fillers:
        text = re.sub(p, '', text)
    # 压缩多余空格
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def clean_corpus_text(raw_content: str) -> str:
    """
    完整清洗工序：判断是否含时间戳 -> 剥离时间戳 -> 去除杂音口癖 -> 规范标点
    """
    if "-->" in raw_content:
        cleaned = strip_srt_timestamps(raw_content)
    else:
        cleaned = raw_content

    cleaned = remove_spoken_fillers(cleaned)
    return cleaned

"""
提词器交付格式化器 (Teleprompter Delivery)
"""

from typing import List
from vbl_koubo.engine.schemas import TeleprompterScript, ScriptSegment
from vbl_koubo.engine.normalizer import (
    normalize_numbers,
    clean_spoken_punctuation,
    calculate_spoken_metrics
)


def format_teleprompter_view(script: TeleprompterScript) -> str:
    """生成带视觉呼吸感的提词器格式文本"""
    lines = [
        f"══════════════════════════════════════════════════",
        f" 🎙️  VBL 口播提词器 | 主题：{script.title}",
        f" 📌  采用风格：{script.skill_used} | 字数：{script.total_words} 字 | 预计：{script.total_estimated_seconds} 秒",
        f"══════════════════════════════════════════════════\n",
    ]

    for seg in script.segments:
        role_label = {
            "hook": "【🔥 黄金钩子 0-3s】",
            "claim": "【🎯 核心定位】",
            "evidence": "【📊 硬核证据】",
            "trade_off": "【⚖️ 代价与边界】",
            "closing": "【🏁 理性收尾】"
        }.get(seg.role, f"【段落 {seg.segment_index}】")

        lines.append(f"{role_label}  ⏱️ {seg.estimated_seconds}s")
        lines.append(f"{seg.marked_text}\n")

    return "\n".join(lines)

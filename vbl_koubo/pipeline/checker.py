"""
L1 静态口播质检哨所 (Static Quality Gate)
借鉴 khazix-writer / koubo-copywriter-lite 工业实践：
对生成的口播稿进行静态分析，零容忍拦截 AI 套话、书面连接腔、假大空与升华模板
"""

from typing import List, Tuple
from dataclasses import dataclass


# 绝对禁词库（命中即判为违规或 AI 味过重）
L1_FORBIDDEN_WORDS = [
    # 总结腔
    "综上所述", "总而言之", "总的来说", "最后我想说", "结语",
    # 连接腔
    "首先", "其次", "再次", "与此同时", "值得一提的是", "毫无疑问",
    # 宏大叙事与万能开头
    "快节奏的时代", "快速发展的时代", "随着科技的发展", "随着社会的发展", "众所周知", "不得不说",
    # 强调腔
    "需要指出的是", "值得注意的是", "我们必须清醒地认识到", "毋庸置疑",
    # 虚假空洞升华
    "不仅让我们看到了", "这不仅仅是", "更是", "人生就是一场",
    # 营销叫卖腔（违背 VBL 客观定位）
    "太炸裂了", "赶紧冲", "必看神器", "彻底颠覆", "史诗级",
]


@dataclass
class QualityCheckResult:
    passed: bool
    violations: List[str]
    clean_text: str


def check_forbidden_words(text: str) -> List[str]:
    """扫描文本中出现的禁词"""
    found = []
    for word in L1_FORBIDDEN_WORDS:
        if word in text:
            found.append(word)
    return found


def sanitize_ai_patterns(text: str) -> str:
    """自动清理或替换常见轻度书面词"""
    replacements = {
        "综上所述，": "",
        "总而言之，": "",
        "总的来说，": "",
        "毋庸置疑，": "",
        "显而易见，": "",
        "鉴于此，": "所以，",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def run_quality_gate(text: str) -> QualityCheckResult:
    """运行质检哨所"""
    sanitized = sanitize_ai_patterns(text)
    violations = check_forbidden_words(sanitized)
    passed = len(violations) == 0
    return QualityCheckResult(
        passed=passed,
        violations=violations,
        clean_text=sanitized
    )

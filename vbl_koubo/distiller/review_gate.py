"""
蒸馏产物机器质检闸 (Review Gate for Blogger Skills)
借鉴 jianxiang 的“机器闸通过不等于审美通过”哲学：
严查 candidate.SKILL.md 是否具备合法 YAML 元数据、Hook 模式数、母结构阶段、禁词表和语速物理约束
杜绝大模型输出空洞无用的形容词废话
"""

import re
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class SkillGateResult:
    passed: bool
    missing_elements: List[str]
    diagnostics: List[str]


def evaluate_candidate_skill(skill_markdown: str) -> SkillGateResult:
    """
    对 candidate.SKILL.md 执行严格的机器硬指标检查：
    1. 必须具备合法的 YAML Frontmatter (含 name, description)
    2. 必须包含 Hook 模式（至少提及 2 种具体开场套路）
    3. 必须包含 叙事母结构 (明确段落阶段推进)
    4. 必须包含 禁忌词表 / 负向约束 (防止空洞无边界)
    5. 必须具备 语速 WPM 或单句字数等物理量化指标
    """
    missing = []
    diagnostics = []

    # 1. 检查 YAML Frontmatter
    if not (skill_markdown.startswith("---") and skill_markdown.count("---") >= 2):
        missing.append("缺少标准 YAML Frontmatter 分界线 (---)")
    else:
        if "name:" not in skill_markdown:
            missing.append("YAML Frontmatter 缺少 name 字段")
        if "description:" not in skill_markdown:
            missing.append("YAML Frontmatter 缺少 description 字段")

    # 2. 检查 Hook 黄金 3 秒规则
    hook_matches = len(re.findall(r'(?:Hook|钩子|切入|开场)', skill_markdown, re.IGNORECASE))
    if hook_matches < 2:
        missing.append("缺少明确的黄金 3 秒 Hook 模式提取")
    else:
        diagnostics.append(f"✓ 识别到 Hook 规则定义 ({hook_matches} 处命中)")

    # 3. 检查叙事母结构
    structure_keywords = ["母结构", "叙事", "展开", "推进", "第 1 段", "第一段", "收尾"]
    struct_hit = any(k in skill_markdown for k in structure_keywords)
    if not struct_hit:
        missing.append("缺少清晰的叙事母结构推进说明")
    else:
        diagnostics.append("✓ 包含叙事母结构阶段推进")

    # 4. 检查负向禁忌词
    negative_keywords = ["禁忌", "负向", "严禁", "避免", "黑名单", "不要"]
    neg_hit = any(k in skill_markdown for k in negative_keywords)
    if not neg_hit:
        missing.append("缺少绝对禁词表或负向语言约束")
    else:
        diagnostics.append("✓ 具备风格排斥词与边界保护")

    # 5. 检查物理量化指标 (WPM 或 字数)
    metric_matches = re.findall(r'(\d{2,3}\s*(?:字|wpm|WPM|秒))', skill_markdown)
    if not metric_matches:
        missing.append("缺少量化物理指标（如建议语速 250字/分 或 单句长度限制）")
    else:
        diagnostics.append(f"✓ 检测到物理约束指标: {', '.join(metric_matches[:3])}")

    passed = len(missing) == 0
    return SkillGateResult(
        passed=passed,
        missing_elements=missing,
        diagnostics=diagnostics
    )


def promote_candidate_to_active(blogger_name: str, skills_dir: Path = None) -> Tuple[bool, str]:
    """
    将通过机器闸的 candidate.SKILL.md 转正为生效的 SKILL.md
    """
    if skills_dir is None:
        skills_dir = Path(__file__).resolve().parent.parent.parent / "skills"

    blogger_dir = skills_dir / blogger_name
    candidate_file = blogger_dir / "candidate.SKILL.md"
    active_file = blogger_dir / "SKILL.md"

    if not candidate_file.exists():
        return False, f"未找到候选技能文件: {candidate_file}"

    content = candidate_file.read_text(encoding="utf-8")
    eval_res = evaluate_candidate_skill(content)
    if not eval_res.passed:
        err_msg = "❌ 机器闸拒绝转正，存在以下硬性缺失:\n" + "\n".join(f"  • {m}" for m in eval_res.missing_elements)
        return False, err_msg

    # 写入转正文件
    active_file.write_text(content, encoding="utf-8")
    return True, f"✅ 验证通过，已成功转正为正式技能: {active_file}"

"""
博主认知逆向蒸馏提取器 (Blogger Pattern Extractor)
遵循 Pattern Extraction Doctrine：
从 2~3 篇清洗后的爆款口播样本中，结构化萃取：人设声线、Hook模型、母结构、高频指纹与物理约束
输出符合标准规范的 candidate.SKILL.md
"""

from pathlib import Path
from typing import List, Optional
from vbl_koubo.distiller.review_gate import evaluate_candidate_skill


DISTILL_SYSTEM_PROMPT = """你是一名资深短视频认知工程架构师与 Agent Skill 专家。
你的任务是从给定的某位博主的真实口播样例文本中，深度逆向提取出该博主的标准化 Skill 契约。

【严禁输出废话】
绝对不要写“语言幽默风趣、生动形象、情感真挚”这类空洞修饰词。
必须提取具体的、可指导大模型复刻写作的硬核规则与句式模式。

【必须提取的 5 大维度】
1. 人设与听觉基调 (Persona & Tone)
2. 黄金 3 秒 Hook 模式（至少总结 2~3 种具体的开场句式模板）
3. 叙事母结构 (Narrative Routing)（从开场到收尾的 4 阶段推进逻辑）
4. 语言指纹与绝对禁词（口头禅、标志过渡词、以及该博主绝不说的词）
5. 节奏与物理指标（建议语速如 250字/分钟，单句字数上限如 16~18字）

【输出格式】
必须严格输出为带有标准 YAML Frontmatter 的完整 Markdown 文档，格式如下：
---
name: blogger-slug-name
description: 一句话精准描述定位与适用场景
version: 1.0.0
author: 博主原名或标识
---

# 博主名称

## 一、 人设与声线定位
...
## 二、 黄金 3 秒钩子特征
...
## 三、 叙事母结构
...
## 四、 语言指纹与禁忌
...
## 五、 节奏与物理指标
...
"""


def build_distill_prompt(blogger_name: str, samples: List[str]) -> str:
    """构建蒸馏提取提示词"""
    joined_samples = "\n\n".join([f"【爆款样本 {i+1}】\n{s}" for i, s in enumerate(samples)])
    return f"""博主代号：{blogger_name}

以下是该博主的真实爆款口播文本：
{joined_samples}

请根据以上素材，输出符合规范的 candidate.SKILL.md 内容："""


def distill_blogger_skill(
    blogger_name: str,
    base_corpus_dir: Optional[Path] = None,
    skills_dir: Optional[Path] = None,
    llm_callable=None
) -> Path:
    """
    端到端执行博主蒸馏：
    读取 corpus/<blogger>/cleaned/*.txt -> 构造 Prompt 提取 -> 写入 skills/<blogger>/candidate.SKILL.md
    """
    if base_corpus_dir is None:
        base_corpus_dir = Path(__file__).resolve().parent.parent.parent / "corpus"
    if skills_dir is None:
        skills_dir = Path(__file__).resolve().parent.parent.parent / "skills"

    cleaned_dir = base_corpus_dir / blogger_name / "cleaned"
    if not cleaned_dir.exists():
        raise FileNotFoundError(f"未找到语料库目录: {cleaned_dir}")

    samples = [f.read_text(encoding="utf-8") for f in cleaned_dir.glob("*.txt") if f.is_file()]
    if not samples:
        raise ValueError(f"语料库 {cleaned_dir} 内没有清洗好的 .txt 样本文本")

    candidate_dir = skills_dir / blogger_name
    candidate_dir.mkdir(parents=True, exist_ok=True)
    candidate_path = candidate_dir / "candidate.SKILL.md"

    if llm_callable:
        prompt = build_distill_prompt(blogger_name, samples)
        skill_text = llm_callable(DISTILL_SYSTEM_PROMPT, prompt)
    else:
        # 确定性基线模板（无真实 API 时提供结构完整的规范草案）
        skill_text = f"""---
name: {blogger_name}
description: 基于 {blogger_name} 爆款语料逆向蒸馏的专属口播技能。
version: 1.0.0
author: {blogger_name}
---

# {blogger_name} 口播风格技能

## 一、 人设与声线定位
- 角色定位：领域实操专家，先讲事实，再给判断。
- 听觉基调：坚定、干脆、节奏紧凑，句尾收敛。

## 二、 黄金 3 秒钩子特征
1. **反常识打脸 Hook**：“很多人以为 [普遍常识]，但真实测试完全相反。”
2. **场景共鸣 Hook**：“如果你今天在做 [具体业务]，真正卡住你的往往是这个隐形问题。”

## 三、 叙事母结构
- 第 1 段：定位与核心主张（承接 Hook，0-8s）
- 第 2 段：硬核证据与数据拆解（展开事实与指标，8-30s）
- 第 3 段：落地路径与代价分析（客观分析边界，30-50s）
- 第 4 段：理性总结收尾（给出可实操结论，50-60s）

## 四、 语言指纹与禁忌
- 标志过渡词：“注意看”、“先看事实”、“核心区别就在这”。
- 绝对禁忌词：严禁使用“在当今快节奏的世界”、“总而言之”、“宛如”、“不可否认”。

## 五、 节奏与物理指标
- 建议语速：240~260 字/分钟。
- 单句长度：严格控制在 18 字以内，杜绝嘴瓢。
"""

    candidate_path.write_text(skill_text.strip(), encoding="utf-8")
    return candidate_path

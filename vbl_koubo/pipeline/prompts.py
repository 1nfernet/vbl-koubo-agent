"""
口播提示词模板引擎 (Prompt Templates)
吸收 broadcast-craft (HKR 黄金钩子竞争模型) 与 koubo-copywriter-lite (去AI味口语写作)
"""

from typing import List
from vbl_koubo.engine.skill_loader import BloggerSkill


def build_hkr_hook_prompt(skill: BloggerSkill, topic_facts: str) -> str:
    """
    构建 HKR 黄金 3 秒钩子竞争提示词：
    要求 LLM 一次性生成 3 种不同心理动机的黄金开头
    """
    return f"""你是一名顶级短视频口播导演。请阅读当前博主的技能规范与核心事实材料，生成 3 组各具杀伤力的黄金 3 秒钩子（Hook）。

【博主技能与人设要求】
名称：{skill.name}
定位与风格：{skill.description}
详细规约：
{skill.content}

【本期核心事实材料】
{topic_facts}

【生成规则】
请严格按照 HKR 坐标系，分别输出 3 种不同心理动机的黄金 Hook（每句 15~25 个字以内，必须适合张口就念）：
1. [H型 - 好奇悬念/颠覆视角]：颠覆常规认知，制造信息差，让听众瞬间停下来。
2. [K型 - 确凿证据/硬核数据]：先抛出震撼具体数字或官方事实，直接用确定性砸向观众。
3. [R型 - 痛点共鸣/工作流反思]：直击观众在实际场景中的困扰与代价，唤起强烈认同。

【输出格式】
必须输出为标准 JSON 格式，如下：
{{
  "hooks": [
    {{
      "type": "H",
      "label": "颠覆认知型",
      "text": "口播文案（纯口语，不超25字）",
      "rationale": "设计意图"
    }},
    {{
      "type": "K",
      "label": "硬核证据型",
      "text": "口播文案（纯口语，不超25字）",
      "rationale": "设计意图"
    }},
    {{
      "type": "R",
      "label": "痛点共鸣型",
      "text": "口播文案（纯口语，不超25字）",
      "rationale": "设计意图"
    }}
  ]
}}
仅输出合法 JSON，不要附带任何前言或反引号。"""


def build_script_body_prompt(skill: BloggerSkill, selected_hook: str, topic_facts: str) -> str:
    """
    构建口播正文生成提示词
    结合选定的黄金 Hook，按照 Skill 定义的母结构推进
    """
    return f"""你是一名专业短视频口播文案创作者。请使用当前博主技能，围绕选定的黄金 Hook 和事实材料，撰写一篇 50~60 秒的完整口播脚本。

【博主规范】
名称：{skill.name}
核心规约：
{skill.content}

【已选定的黄金 3 秒开头 (Hook)】
"{selected_hook}"

【事实材料】
{topic_facts}

【写作铁律】
1. 去 AI 味：坚决不用“在当今快节奏的时代”、“综上所述”、“不仅如此”、“让我们拭目以待”。
2. 气口短句：单句长度不超过 16 字，多用短句、断句，允许口语停顿。
3. 遵循博主母结构推进：
   - 第 1 段：定位与核心主张（承接 Hook，0-8s）
   - 第 2 段：硬核证据与数据拆解（抛出事实，8-30s）
   - 第 3 段：落地路径与代价/限制（客观公正，30-50s）
   - 第 4 段：理性总结收尾（留给观众思考，50-60s）
4. 语言要求：像真人坐在镜头前跟朋友对话，冷静、笃定、字字有回音。

【输出格式】
请输出为纯连贯口播文案，每句话单独成行，不带段落标签，不带任何解释。"""

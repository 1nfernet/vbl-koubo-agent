"""
端到端口播生成编排流水线 (Orchestrator)
串联：博主技能加载 -> HKR 黄金钩子竞争 -> 4 步母结构展开 -> L1 静态质检哨所 -> 确定性发音与提词排版
"""

import os
import re
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from vbl_koubo.engine.skill_loader import BloggerSkill, load_skill_by_name
from vbl_koubo.engine.normalizer import (
    normalize_numbers,
    clean_spoken_punctuation,
    split_into_breath_chunks,
    calculate_spoken_metrics
)
from vbl_koubo.engine.schemas import TeleprompterScript, ScriptSegment
from vbl_koubo.pipeline.prompts import build_hkr_hook_prompt, build_script_body_prompt
from vbl_koubo.pipeline.checker import run_quality_gate, QualityCheckResult


def extract_json_from_response(raw_text: str) -> Optional[Dict[str, Any]]:
    """
    防御性解析大模型返回的 JSON：
    能自动剔除外层的 ```json ... ``` 或 ``` ... ``` Markdown 围栏，
    并提取出内部的合法 JSON 对象
    """
    cleaned = raw_text.strip()
    # 剥离 markdown 代码围栏
    if cleaned.startswith("```"):
        cleaned = re.sub(r'^```[a-zA-Z]*\n', '', cleaned)
        cleaned = re.sub(r'\n```$', '', cleaned)
        cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except Exception:
        # 如果依然失败，尝试用正则找到最外层的 { ... }
        match = re.search(r'(\{[\s\S]*\})', cleaned)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
    return None


@dataclass
class HookCandidate:
    type: str
    label: str
    text: str
    rationale: str


class KouboOrchestrator:
    """口播端到端流水线控制器"""

    def __init__(self, skill_name: str = "vbl-rational"):
        self.skill: BloggerSkill = load_skill_by_name(skill_name)

    def generate_hooks(self, facts: str, llm_callable=None) -> List[HookCandidate]:
        """
        生成 HKR 黄金 3 秒钩子候选
        如果提供了 llm_callable 则调用真实 LLM，否则运行规则基线
        """
        if llm_callable:
            prompt = build_hkr_hook_prompt(self.skill, facts)
            raw_response = llm_callable(prompt)
            data = extract_json_from_response(raw_response)
            if data and "hooks" in data:
                hooks = []
                for item in data.get("hooks", []):
                    hooks.append(HookCandidate(
                        type=item.get("type", "H"),
                        label=item.get("label", "候选钩子"),
                        text=normalize_numbers(item.get("text", "")),
                        rationale=item.get("rationale", "")
                    ))
                if hooks:
                    return hooks

        # 降级 / 确定性基线生成
        title_snippet = facts.split("\n")[0][:20].strip("# ")
        return [
            HookCandidate(
                type="H",
                label="颠覆认知型",
                text=normalize_numbers(f"大多数人以为这只是常规升级，但这次事实完全不同。"),
                rationale="制造信息落差，留住好奇用户"
            ),
            HookCandidate(
                type="K",
                label="硬核证据型",
                text=normalize_numbers(f"先看一组官方确凿数据：新一代指标提升了近百分之五十。"),
                rationale="数据直给，适合理性与技术受众"
            ),
            HookCandidate(
                type="R",
                label="痛点共鸣型",
                text=normalize_numbers(f"如果今天要在生产环境落地，真正卡住你的不是算法本身。"),
                rationale="切入落地实操痛点，引发同理心"
            )
        ]

    def build_teleprompter_script(
        self,
        title: str,
        selected_hook: str,
        body_text: str
    ) -> TeleprompterScript:
        """
        后处理物理层：过筛禁词、数字发音汉化、长句切分、测算时长并组装提词器
        """
        # 1. 质量哨所检查
        full_raw = f"{selected_hook}\n{body_text}"
        gate_res: QualityCheckResult = run_quality_gate(full_raw)
        clean_base = gate_res.clean_text

        # 2. 物理层发音规范化与标点清理
        spoken_text = normalize_numbers(clean_base)
        spoken_text = clean_spoken_punctuation(spoken_text)

        # 3. 气口切分
        raw_chunks = split_into_breath_chunks(spoken_text, max_chars=18)
        
        segments: List[ScriptSegment] = []
        for idx, chunk in enumerate(raw_chunks, 1):
            chunk_clean = chunk.strip("，。！？ ")
            if not chunk_clean:
                continue
            
            # 简易角色标注
            role = "hook" if idx <= 2 else ("closing" if idx >= len(raw_chunks) - 1 else "evidence")
            c_count, sec = calculate_spoken_metrics(chunk_clean, wpm=250)
            
            # 为提词器生成视觉加粗（简单将首个关键信息加粗）
            marked = f"{chunk_clean}。" if not chunk.endswith("。") else chunk
            if "百分之" in chunk_clean or "点" in chunk_clean:
                marked = f"**{marked}**"

            segments.append(ScriptSegment(
                segment_index=idx,
                role=role,
                spoken_text=chunk_clean,
                marked_text=marked,
                emphasis_words=[],
                estimated_seconds=sec
            ))

        total_words, total_seconds = calculate_spoken_metrics(spoken_text, wpm=250)

        # 格式化提词器文本（包含轻量可复现 Manifest）
        import datetime
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        teleprompter_lines = [
            f"/* RUN MANIFEST */",
            f"/* Generated: {timestamp_str} | Skill: {self.skill.name} v{self.skill.version} */",
            f"/* Standard WPM: 250 | Segments: {len(segments)} */\n",
            f"🎙️ 【{title}】 | 风格：{self.skill.name}",
            f"⏱️ 预计总长：{total_seconds} 秒 | 总字数：{total_words} 字\n",
            "──────────────────────────────────────────"
        ]
        for seg in segments:
            cue_tag = "【🔥 黄金钩子】" if seg.role == "hook" else ("【🏁 理性收尾】" if seg.role == "closing" else "【📌 论据展开】")
            teleprompter_lines.append(f"{cue_tag} ({seg.estimated_seconds}s)")
            teleprompter_lines.append(f"  {seg.marked_text}\n")

        return TeleprompterScript(
            title=title,
            skill_used=self.skill.name,
            total_words=total_words,
            total_estimated_seconds=total_seconds,
            wpm_standard=250,
            segments=segments,
            clean_voice_text=spoken_text,
            teleprompter_text="\n".join(teleprompter_lines)
        )

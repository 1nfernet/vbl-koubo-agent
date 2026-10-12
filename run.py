"""
VBL 口播 Agent 命令行极简入口 (CLI Entry)
可在无需复杂配置下即刻体验核心口播规约与提词预览
"""

import sys
from pathlib import Path

from vbl_koubo.engine.skill_loader import list_available_skills, load_skill_by_name
from vbl_koubo.engine.normalizer import (
    normalize_numbers,
    clean_spoken_punctuation,
    split_into_breath_chunks,
    calculate_spoken_metrics
)


def run_demo():
    print("=" * 60)
    print("🎙️  欢迎使用 VBL 口播 Agent (vbl-koubo-agent)")
    print("=" * 60)

    # 1. 扫描当前 Skills
    skills = list_available_skills()
    print(f"\n[1] 正在检索已沉淀的博主 Skills 库...")
    for name, skill in skills.items():
        print(f"  • [{name}] - {skill.description} (by {skill.author or 'Unknown'})")

    # 2. 模拟加载 vbl-rational
    active_skill = load_skill_by_name("vbl-rational")
    print(f"\n[2] 默认激活风格：[{active_skill.name}]")

    # 3. 示例原始输入文本
    raw_draft = (
        "这里是VBL。本期看GPT-6 Astra。OpenAI把它定位为新一代智能模型，"
        "重点是把电脑操作、浏览、软件工程与专业工作放进同一个工作流。"
        "官方页面给出的结果很具体：OSWorld 2.0得分72.6%，ScreenSpot-Pro 92.7%，"
        "Terminal-Bench 4.0为57.9%。在专业任务上，AutomationBench 41.4%，BenchCAD 95.9%。"
        "API标准价是每百万输入token 10美元、每百万输出token 50美元；快速模式按标准价2倍计费。"
        "先看页面证据，再决定它适不适合你的工作流。"
    )

    print("\n[3] 原始输入素材：")
    print("-" * 50)
    print(raw_draft)
    print("-" * 50)

    # 4. 经过物理引擎 Normalizer 转换
    spoken = normalize_numbers(raw_draft)
    spoken = clean_spoken_punctuation(spoken)
    char_count, est_seconds = calculate_spoken_metrics(spoken, wpm=250)

    print(f"\n[4] 规范化口播稿 (数字转汉字发音 / 符号清洗)：")
    print("-" * 50)
    print(spoken)
    print("-" * 50)
    print(f"📊 统计：有效字数 {char_count} 字 | 预计朗读时长 {est_seconds} 秒 (标准语速 250字/分)")

    # 5. 气口切分演示（提词器分行）
    chunks = split_into_breath_chunks(spoken, max_chars=18)
    print("\n[5] 提词器气口排版预览（单句 <= 18字）：")
    print("-" * 50)
    for idx, chunk in enumerate(chunks, 1):
        print(f"  {idx:02d} | {chunk}")
    print("-" * 50)


if __name__ == "__main__":
    run_demo()

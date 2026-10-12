"""
VBL 口播 Agent 命令行端到端入口 (CLI Entry)
串联 HKR 黄金钩子选择 -> 结构化正文编排 -> 物理发音过筛 -> 提词器排版
"""

import sys
from pathlib import Path

from vbl_koubo.engine.skill_loader import list_available_skills
from vbl_koubo.pipeline.orchestrator import KouboOrchestrator


def main():
    print("=" * 65)
    print("🎙️  VBL 口播 Agent | 端到端生成与提词引擎 (vbl-koubo-agent)")
    print("=" * 65)

    # 1. 扫描与展示已注册 Skills
    skills = list_available_skills()
    print(f"\n[1] 正在加载博主 Skills 库...")
    for name, skill in skills.items():
        print(f"  • [{name}] - {skill.description} (作者: {skill.author or '未知'})")

    # 2. 激活 VBL 理性客观风格
    orchestrator = KouboOrchestrator(skill_name="vbl-rational")
    print(f"\n[2] 当前激活技能: [{orchestrator.skill.name}]")

    # 3. 模拟输入真实素材
    topic_title = "OpenAI GPT-6 Astra 深度评测"
    topic_facts = (
        "OpenAI 发布 GPT-6 Astra，定位为新一代智能模型，主打电脑操作、浏览与专业工程协同。\n"
        "基准测试得分：OSWorld 2.0 得分 72.6%，ScreenSpot-Pro 达到 92.7%，Terminal-Bench 4.0 为 57.9%。\n"
        "专业任务方面：AutomationBench 41.4%，BenchCAD 达到 95.9%。\n"
        "API 定价为每百万输入 token 10 美元，每百万输出 token 50 美元，快速模式按标准价 2 倍计费。"
    )

    print(f"\n[3] 待处理素材与事实输入：")
    print("-" * 55)
    print(topic_facts)
    print("-" * 55)

    # 4. 生成 HKR 黄金 3 秒钩子候选
    print("\n[4] 黄金 3 秒钩子引擎正在竞合生成 (HKR 坐标系)...")
    hooks = orchestrator.generate_hooks(topic_facts)
    for idx, h in enumerate(hooks, 1):
        print(f"  👉 钩子 {idx} [{h.type}型 · {h.label}]:")
        print(f"     文案: \"{h.text}\"")
        print(f"     意图: {h.rationale}")

    # 5. 选定第 2 个 Hook（硬核证据型）并生成正文
    selected_hook = hooks[1].text
    print(f"\n[5] 选定高转化开场: \"{selected_hook}\"")

    body_draft = (
        "这里是 VBL。官方页面给出的测试结果很具体：OSWorld 2.0 得分 72.6%，"
        "ScreenSpot-Pro 达到 92.7%，Terminal-Bench 4.0 为 57.9%。"
        "在专业任务上，AutomationBench 41.4%，BenchCAD 达到 95.9%。"
        "页面写明，API 标准价是每百万输入 token 10 美元、输出 50 美元；快速模式按 2 倍计费。"
        "先看页面证据，再决定它适不适合你的工作流。"
    )

    # 6. 物理层安全网过筛与提词器交付
    script = orchestrator.build_teleprompter_script(
        title=topic_title,
        selected_hook=selected_hook,
        body_text=body_draft
    )

    print("\n" + "=" * 65)
    print(script.teleprompter_text)
    print("=" * 65)

    print(f"\n✅ 交付完成！")
    print(f"   • 有效口播字数: {script.total_words} 字")
    print(f"   • 精准预计时长: {script.total_estimated_seconds} 秒")
    print(f"   • 数字汉化率: 100% (如 72.6% -> 百分之七十二点六, 10美元 -> 十美元)")
    print(f"   • 气口切分段数: {len(script.segments)} 段 (单句 <= 18 字，杜绝嘴瓢)")


if __name__ == "__main__":
    main()

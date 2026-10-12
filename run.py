"""
VBL 口播 Agent 命令行端到端入口 (CLI Entry)
串联：
1. 环境能力检查（yt-dlp 等）
2. 博主语料摄取与清洗 (corpus/raw -> cleaned)
3. 认知逆向蒸馏 (distiller -> candidate.SKILL.md)
4. 机器质检闸审查与转正 (review_gate -> SKILL.md)
5. 端到端口播提词生成与确定性归档 (output/<YYYY-MM-DD>_<slug>/)
"""

import sys
import datetime
import re
from pathlib import Path

from vbl_koubo.engine.skill_loader import list_available_skills
from vbl_koubo.pipeline.orchestrator import KouboOrchestrator
from vbl_koubo.distiller.ingest import ingest_from_text, check_ytdlp_available
from vbl_koubo.distiller.extractor import distill_blogger_skill
from vbl_koubo.distiller.review_gate import promote_candidate_to_active


def slugify(text: str) -> str:
    """生成合规的目录 slug"""
    slug = re.sub(r'[^\w\u4e00-\u9fa5]+', '-', text).strip('-')
    return slug[:30] or "untitled"


def main():
    print("=" * 65)
    print("🎙️  VBL 口播 Agent (vbl-koubo-agent) | 架构与全功能工作流")
    print("=" * 65)

    # 1. 检查环境能力
    ytdlp_ok = check_ytdlp_available()
    print(f"\n[1] 运行环境能力体检:")
    print(f"  • yt-dlp 字幕抽取支持: {'✅ 已就绪 (可无损秒提字幕)' if ytdlp_ok else '⚠️ 未就绪 (支持手动文本录入降级)'}")

    # 2. 演示：博主认知逆向蒸馏闭环 (Distillation Cycle)
    print(f"\n[2] 演示：博主认知逆向蒸馏闭环 (Distillation Cycle):")
    blogger = "commercial-master"
    raw_sample = (
        "1\n00:00:01,000 --> 00:00:03,000\n很多人做自媒体总以为是文案写不好。\n\n"
        "2\n00:00:03,500 --> 00:00:06,000\n实际上真正卡住你的是没有搞懂转化路径！\n\n"
        "3\n00:00:06,500 --> 00:00:10,000\n注意看，先看数据，前3秒完播率只有10%你怎么卖货？先看事实！"
    )
    cleaned_path = ingest_from_text(raw_sample, blogger_name=blogger, sample_name="sample1")
    print(f"  • 原始 SRT 语料已摄取并完成清洗: {cleaned_path}")

    # 执行蒸馏
    candidate_path = distill_blogger_skill(blogger_name=blogger)
    print(f"  • 已逆向提取该博主认知契约: {candidate_path}")

    # 机器质检闸审核转正
    success, msg = promote_candidate_to_active(blogger)
    print(f"  • 机器质检闸审查结果: {msg}")

    # 3. 扫描已生效 Skills
    skills = list_available_skills()
    print(f"\n[3] 当前已生效的博主 Skills 库:")
    for name, skill in skills.items():
        print(f"  • [{name}] - {skill.description} (作者: {skill.author or '未知'})")

    # 4. 激活 VBL 理性风格执行口播生成
    orchestrator = KouboOrchestrator(skill_name="vbl-rational")
    print(f"\n[4] 激活技能: [{orchestrator.skill.name}]")

    topic_title = "OpenAI GPT-6 Astra 深度评测"
    topic_facts = (
        "OpenAI 发布 GPT-6 Astra，定位为新一代智能模型，主打电脑操作、浏览与专业工程协同。\n"
        "基准测试得分：OSWorld 2.0 得分 72.6%，ScreenSpot-Pro 达到 92.7%，Terminal-Bench 4.0 为 57.9%。\n"
        "专业任务方面：AutomationBench 41.4%，BenchCAD 达到 95.9%。\n"
        "API 定价为每百万输入 token 10 美元，每百万输出 token 50 美元，快速模式按标准价 2 倍计费。"
    )

    hooks = orchestrator.generate_hooks(topic_facts)
    selected_hook = hooks[1].text  # 选定硬核证据型

    body_draft = (
        "这里是 VBL。官方页面给出的测试结果很具体：OSWorld 2.0 得分 72.6%，"
        "ScreenSpot-Pro 达到 92.7%，Terminal-Bench 4.0 为 57.9%。"
        "在专业任务上，AutomationBench 41.4%，BenchCAD 达到 95.9%。"
        "页面写明，API 标准价是每百万输入 token 10 美元、输出 50 美元；快速模式按 2 倍计费。"
        "先看页面证据，再决定它适不适合你的工作流。"
    )

    script = orchestrator.build_teleprompter_script(
        title=topic_title,
        selected_hook=selected_hook,
        body_text=body_draft
    )

    # 5. 确定性输出归档规范：output/<YYYY-MM-DD>_<slug>/
    today_str = datetime.date.today().isoformat()
    folder_slug = f"{today_str}_{slugify(topic_title)}"
    out_dir = Path("output") / folder_slug
    out_dir.mkdir(parents=True, exist_ok=True)

    tele_file = out_dir / "teleprompter.txt"
    vo_file = out_dir / "vo-final.txt"

    tele_file.write_text(script.teleprompter_text, encoding="utf-8")
    vo_file.write_text(script.clean_voice_text, encoding="utf-8")

    print("\n" + "=" * 65)
    print(script.teleprompter_text)
    print("=" * 65)

    print(f"\n✅ 交付与归档完成！")
    print(f"   • 规范归档目录: {out_dir}")
    print(f"   • 提词器交付文件: {tele_file}")
    print(f"   • 纯净口播稿 (vo-final.txt): {vo_file}")
    print(f"   • 字数/预计耗时: {script.total_words} 字 / {script.total_estimated_seconds} 秒")


if __name__ == "__main__":
    main()

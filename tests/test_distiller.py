"""
蒸馏体系测试套件：清洗器、机器质检闸、候选转正机制
"""

import unittest
from pathlib import Path
import tempfile
import shutil

from vbl_koubo.distiller.cleaner import strip_srt_timestamps, remove_spoken_fillers, clean_corpus_text
from vbl_koubo.distiller.review_gate import evaluate_candidate_skill, promote_candidate_to_active
from vbl_koubo.distiller.ingest import ingest_from_text
from vbl_koubo.distiller.extractor import distill_blogger_skill


class TestDistiller(unittest.TestCase):

    def test_strip_srt_timestamps(self):
        srt = (
            "1\n"
            "00:00:01,000 --> 00:00:03,500\n"
            "这里是 VBL 频道。\n\n"
            "2\n"
            "00:00:03,600 --> 00:00:06,000\n"
            "本期看 GPT 六 Astra。\n"
        )
        cleaned = strip_srt_timestamps(srt)
        self.assertNotIn("-->", cleaned)
        self.assertNotIn("00:00:01", cleaned)
        self.assertIn("这里是 VBL 频道。", cleaned)
        self.assertIn("本期看 GPT 六 Astra。", cleaned)

    def test_remove_spoken_fillers(self):
        raw = "那个那个 我们今天要聊聊 呃 这个技术 啊"
        cleaned = remove_spoken_fillers(raw)
        self.assertNotIn("那个那个", cleaned)
        self.assertNotIn("呃", cleaned)

    def test_review_gate_validation(self):
        # 完备合规的 Skill
        valid_skill = """---
name: sample-blogger
description: 测试博主
version: 1.0.0
author: 测试
---
# 标题
## 一、 人设
## 二、 黄金 3 秒钩子
- Hook 模式 A
- Hook 模式 B
## 三、 叙事母结构展开
- 第一段
## 四、 绝对禁忌词表
- 避免空洞
## 五、 节奏与物理指标
- 建议语速 250字/分钟
"""
        res = evaluate_candidate_skill(valid_skill)
        self.assertTrue(res.passed, f"预期通过，实际未通过: {res.missing_elements}")

        # 缺少核心要素的不合规 Skill（空洞形容词堆叠）
        bad_skill = """# 某个博主
他说话幽默风趣，非常具有吸引力，我很喜欢他。
"""
        bad_res = evaluate_candidate_skill(bad_skill)
        self.assertFalse(bad_res.passed)
        self.assertGreater(len(bad_res.missing_elements), 2)

    def test_full_distill_and_promotion_cycle(self):
        # 在临时目录测试完整生命周期
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            corpus_dir = tmp_path / "corpus"
            skills_dir = tmp_path / "skills"

            # 1. 语料入库
            ingest_from_text(
                text_content="这里是测试博主。第一点事实。第二点证据。结尾总结。",
                blogger_name="tech-tester",
                sample_name="sample1",
                base_corpus_dir=corpus_dir
            )

            # 2. 执行蒸馏
            candidate_path = distill_blogger_skill(
                blogger_name="tech-tester",
                base_corpus_dir=corpus_dir,
                skills_dir=skills_dir
            )
            self.assertTrue(candidate_path.exists())
            self.assertEqual(candidate_path.name, "candidate.SKILL.md")

            # 3. 机器闸转正
            success, msg = promote_candidate_to_active("tech-tester", skills_dir=skills_dir)
            self.assertTrue(success, f"转正失败: {msg}")
            
            # 转正后应生成正式 SKILL.md
            active_file = skills_dir / "tech-tester" / "SKILL.md"
            self.assertTrue(active_file.exists())

    def test_package_skill_exporter(self):
        # 测试将指定 skill 打包为独立可分发单包的能力
        from vbl_koubo.distiller.packager import package_skill
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            mock_skills = tmp_path / "skills"
            mock_dist = tmp_path / "dist"
            
            # 创建模拟合法 skill
            s_dir = mock_skills / "demo-skill"
            s_dir.mkdir(parents=True)
            (s_dir / "SKILL.md").write_text("---\nname: demo-skill\ndescription: demo\n---\n# Demo\n", encoding="utf-8")

            # 导出为独立目录
            ok, msg = package_skill("demo-skill", skills_dir=mock_skills, output_dir=mock_dist, as_zip=False)
            self.assertTrue(ok)
            self.assertTrue((mock_dist / "demo-skill" / "SKILL.md").exists())

            # 导出为 Zip
            ok_zip, msg_zip = package_skill("demo-skill", skills_dir=mock_skills, output_dir=mock_dist, as_zip=True)
            self.assertTrue(ok_zip)
            self.assertTrue((mock_dist / "demo-skill.zip").exists())


if __name__ == "__main__":
    unittest.main()

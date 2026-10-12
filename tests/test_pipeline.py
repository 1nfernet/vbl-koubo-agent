"""
Pipeline 编排与质检单元测试
"""

import unittest
from vbl_koubo.pipeline.checker import run_quality_gate, check_forbidden_words
from vbl_koubo.pipeline.orchestrator import KouboOrchestrator


class TestPipeline(unittest.TestCase):

    def test_forbidden_words_detection(self):
        bad_text = "综上所述，在这个快节奏的时代，这个技术太炸裂了，毫无疑问不仅如此。"
        violations = check_forbidden_words(bad_text)
        self.assertIn("综上所述", violations)
        self.assertIn("快节奏的时代", violations)
        self.assertIn("太炸裂了", violations)
        self.assertIn("毫无疑问", violations)

    def test_quality_gate_sanitization(self):
        text_with_crap = "总而言之，我们需要关注事实。鉴于此，先看数据。"
        res = run_quality_gate(text_with_crap)
        self.assertNotIn("总而言之", res.clean_text)
        self.assertIn("所以，先看数据", res.clean_text)

    def test_orchestrator_generate_hooks(self):
        orch = KouboOrchestrator(skill_name="vbl-rational")
        facts = "产品更新：GPT-6 发布，OSWorld 得分 72.6%"
        hooks = orch.generate_hooks(facts)
        self.assertEqual(len(hooks), 3)
        types = [h.type for h in hooks]
        self.assertIn("H", types)
        self.assertIn("K", types)
        self.assertIn("R", types)

    def test_extract_json_from_markdown_fence(self):
        # 测试防崩溃提取：带 markdown ```json 围栏的大模型返回
        from vbl_koubo.pipeline.orchestrator import extract_json_from_response
        wrapped_json = "```json\n{\"hooks\": [{\"type\": \"H\", \"label\": \"测试\", \"text\": \"文案\", \"rationale\": \"意图\"}]}\n```"
        data = extract_json_from_response(wrapped_json)
        self.assertIsNotNone(data)
        self.assertIn("hooks", data)
        self.assertEqual(data["hooks"][0]["type"], "H")

    def test_orchestrator_build_teleprompter(self):
        orch = KouboOrchestrator(skill_name="vbl-rational")
        hook = "这里是VBL。先看一组确凿证据。"
        body = "官方页面显示，得分达到 72.6%，价格为 10 美元。先看页面证据，再决定它适不适合你的工作流。"
        script = orch.build_teleprompter_script("GPT-6评测", hook, body)

        self.assertIn("百分之七十二点六", script.clean_voice_text)
        self.assertIn("十美元", script.clean_voice_text)
        self.assertGreater(script.total_words, 20)
        self.assertGreater(script.total_estimated_seconds, 5.0)
        self.assertGreater(len(script.segments), 2)


if __name__ == "__main__":
    unittest.main()

"""
使用 Python 标准库 unittest 进行无外部依赖的核心测试
"""

import unittest
from pathlib import Path

from vbl_koubo.engine.normalizer import (
    normalize_numbers,
    clean_spoken_punctuation,
    split_into_breath_chunks,
    calculate_spoken_metrics,
    _int_to_chinese
)
from vbl_koubo.engine.skill_loader import load_skill_by_name, list_available_skills


class TestVBLKouboCore(unittest.TestCase):

    def test_int_to_chinese(self):
        self.assertEqual(_int_to_chinese("0"), "零")
        self.assertEqual(_int_to_chinese("5"), "五")
        self.assertEqual(_int_to_chinese("15"), "十五")
        self.assertEqual(_int_to_chinese("108"), "一百零八")
        self.assertEqual(_int_to_chinese("1200"), "一千二百")

    def test_normalize_numbers(self):
        # 测试百分比转换
        res = normalize_numbers("OSWorld 2.0 得分 72.6%")
        self.assertIn("百分之七十二点六", res)
        # 测试小数转换
        self.assertIn("二点零", res)
        # 测试整数
        res_int = normalize_numbers("输出 50 美元")
        self.assertIn("五十", res_int)

    def test_clean_spoken_punctuation(self):
        raw = "关键指标如下：准确率（综合）达到 90%；不仅如此——还有新特性。"
        cleaned = clean_spoken_punctuation(raw)
        self.assertNotIn("：", cleaned)
        self.assertNotIn("；", cleaned)
        self.assertNotIn("（", cleaned)
        self.assertNotIn("——", cleaned)

    def test_split_into_breath_chunks(self):
        long_sentence = "这里是VBL，今天我们来看OpenAI最新发布的模型，重点是把电脑操作和软件工程放进同一个工作流。"
        chunks = split_into_breath_chunks(long_sentence, max_chars=18)
        self.assertGreaterEqual(len(chunks), 2)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 22)

    def test_calculate_spoken_metrics(self):
        text = "这里是VBL。本期看GPT六Astra。"
        count, seconds = calculate_spoken_metrics(text, wpm=250)
        self.assertGreater(count, 0)
        self.assertGreater(seconds, 0.0)

    def test_load_skill(self):
        skill = load_skill_by_name("vbl-rational")
        self.assertEqual(skill.name, "vbl-rational")
        self.assertIn("冷静带人看懂", skill.content)
        self.assertEqual(skill.author, "VBL")

    def test_list_skills(self):
        skills = list_available_skills()
        self.assertIn("vbl-rational", skills)
        self.assertNotIn("_template", skills)


if __name__ == "__main__":
    unittest.main()

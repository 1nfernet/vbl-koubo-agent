"""
统一 LLM 调用与配置层 (LLM Provider)
支持 DeepSeek, OpenAI, Claude 等模型，提供结构化 Prompt 调用
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")


def get_llm_config() -> Dict[str, Any]:
    """读取当前环境变量配置"""
    return {
        "model": DEFAULT_MODEL,
        "api_key": os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY"),
        "api_base": os.getenv("OPENAI_BASE_URL") or os.getenv("DEEPSEEK_BASE_URL"),
    }

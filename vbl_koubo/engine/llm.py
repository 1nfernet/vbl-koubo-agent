"""
统一 LLM 调用与配置层 (LLM Provider)
支持 DeepSeek, OpenAI, Moonshot 等所有兼容 OpenAI 接口的模型
采用 Python 原生 urllib.request 实现，零第三方库强依赖，开箱即用且高度可移植
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # 优雅降级：在未安装 python-dotenv 环境下依然支持原生 os.environ 读取
    pass

DEFAULT_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
DEFAULT_BASE_URL = os.getenv("DEEPSEEK_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "https://api.deepseek.com"
DEFAULT_API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")


def get_llm_config() -> Dict[str, Any]:
    """读取当前环境变量配置"""
    return {
        "model": os.getenv("LLM_MODEL", DEFAULT_MODEL),
        "api_key": os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY") or "",
        "api_base": os.getenv("DEEPSEEK_BASE_URL") or os.getenv("OPENAI_BASE_URL") or DEFAULT_BASE_URL,
    }


def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.7,
    timeout: int = 60
) -> str:
    """
    通用 LLM 调用客户端
    支持任何 OpenAI 兼容的 API（如 DeepSeek、Kimi、OpenAI）
    """
    cfg = get_llm_config()
    final_model = model or cfg["model"]
    # 兼容去掉前缀（如 deepseek/deepseek-chat -> deepseek-chat）
    if "/" in final_model:
        final_model = final_model.split("/")[-1]

    final_key = api_key or cfg["api_key"]
    final_base = (base_url or cfg["api_base"]).rstrip("/")
    if not final_base.endswith("/v1"):
        final_endpoint = f"{final_base}/chat/completions"
    else:
        final_endpoint = f"{final_base}/chat/completions"

    if not final_key:
        raise ValueError(
            "未检测到 LLM API Key！请在根目录 .env 文件中配置 DEEPSEEK_API_KEY 或 OPENAI_API_KEY。"
        )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": final_model,
        "messages": messages,
        "temperature": temperature,
        "stream": False
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        final_endpoint,
        data=req_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {final_key}",
            "User-Agent": "vbl-koubo-agent/0.1.0"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_body = resp.read().decode("utf-8")
            data = json.loads(resp_body)
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"LLM API 请求失败 HTTP {e.code}: {error_body}")
    except Exception as e:
        raise RuntimeError(f"调用 LLM 发生网络或解析异常: {str(e)}")

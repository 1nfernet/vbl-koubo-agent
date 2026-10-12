"""
核心数据契约层 (Schemas)
定义从选题事实、Hook候选、分段草稿到最终提词器输出的标准数据模型
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class TopicFact(BaseModel):
    """选题与事实契约"""
    title: str = Field(..., description="选题标题")
    core_claim: str = Field(..., description="核心主张/一句话论点")
    evidence_points: List[str] = Field(default_factory=list, description="确凿证据与数据点列表")
    target_audience: Optional[str] = Field(None, description="目标受众画像")


class HookOption(BaseModel):
    """黄金 3 秒钩子选项"""
    hook_type: str = Field(..., description="钩子类型，如：反常识/直击痛点/定位先行")
    content: str = Field(..., description="钩子口播文案（口语化）")
    duration_seconds: float = Field(default=3.0, description="预估时长（秒）")


class ScriptSegment(BaseModel):
    """口播稿单段"""
    segment_index: int = Field(..., description="段落索引（从1开始）")
    role: str = Field(..., description="段落角色：hook / claim / evidence / trade_off / closing")
    spoken_text: str = Field(..., description="规范化后的纯口语文字")
    marked_text: str = Field(..., description="带【重音】与【停顿】的提词器文本")
    emphasis_words: List[str] = Field(default_factory=list, description="该句主重音词")
    estimated_seconds: float = Field(..., description="预估朗读时长（秒）")


class TeleprompterScript(BaseModel):
    """交付态完整口播脚本"""
    title: str = Field(..., description="视频主题")
    skill_used: str = Field(..., description="所采用的博主 Skill 名称")
    total_words: int = Field(..., description="总字数（中文字符数）")
    total_estimated_seconds: float = Field(..., description="总预估时长（秒）")
    wpm_standard: int = Field(default=250, description="参考语速（字/分钟）")
    segments: List[ScriptSegment] = Field(default_factory=list, description="分段明细")
    clean_voice_text: str = Field(..., description="纯净无标记连贯稿（用于TTS或vo-final.txt）")
    teleprompter_text: str = Field(..., description="完整排版提词器文本")

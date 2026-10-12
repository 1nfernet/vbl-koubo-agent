"""
核心数据契约层 (Schemas)
定义从选题事实、Hook候选、分段草稿到最终提词器输出的标准数据模型
提供 dataclass 零外部依赖基类，在 pydantic 存在时无缝增强
"""

from typing import List, Optional
from dataclasses import dataclass, field

try:
    from pydantic import BaseModel, Field
    _USE_PYDANTIC = True
except ImportError:
    _USE_PYDANTIC = False


if _USE_PYDANTIC:
    class TopicFact(BaseModel):
        title: str = Field(..., description="选题标题")
        core_claim: str = Field(..., description="核心主张/一句话论点")
        evidence_points: List[str] = Field(default_factory=list, description="确凿证据与数据点列表")
        target_audience: Optional[str] = Field(None, description="目标受众画像")

    class HookOption(BaseModel):
        hook_type: str = Field(..., description="钩子类型，如：反常识/直击痛点/定位先行")
        content: str = Field(..., description="钩子口播文案（口语化）")
        duration_seconds: float = Field(default=3.0, description="预估时长（秒）")

    class ScriptSegment(BaseModel):
        segment_index: int = Field(..., description="段落索引（从1开始）")
        role: str = Field(..., description="段落角色：hook / claim / evidence / trade_off / closing")
        spoken_text: str = Field(..., description="规范化后的纯口语文字")
        marked_text: str = Field(..., description="带【重音】与【停顿】的提词器文本")
        emphasis_words: List[str] = Field(default_factory=list, description="该句主重音词")
        estimated_seconds: float = Field(..., description="预估朗读时长（秒）")

    class TeleprompterScript(BaseModel):
        title: str = Field(..., description="视频主题")
        skill_used: str = Field(..., description="所采用的博主 Skill 名称")
        total_words: int = Field(..., description="总字数（中文字符数）")
        total_estimated_seconds: float = Field(..., description="总预估时长（秒）")
        wpm_standard: int = Field(default=250, description="参考语速（字/分钟）")
        segments: List[ScriptSegment] = Field(default_factory=list, description="分段明细")
        clean_voice_text: str = Field(..., description="纯净无标记连贯稿（用于TTS或vo-final.txt）")
        teleprompter_text: str = Field(..., description="完整排版提词器文本")

else:
    @dataclass
    class TopicFact:
        title: str
        core_claim: str
        evidence_points: List[str] = field(default_factory=list)
        target_audience: Optional[str] = None

    @dataclass
    class HookOption:
        hook_type: str
        content: str
        duration_seconds: float = 3.0

    @dataclass
    class ScriptSegment:
        segment_index: int
        role: str
        spoken_text: str
        marked_text: str
        emphasis_words: List[str] = field(default_factory=list)
        estimated_seconds: float = 0.0

    @dataclass
    class TeleprompterScript:
        title: str
        skill_used: str
        total_words: int
        total_estimated_seconds: float
        clean_voice_text: str
        teleprompter_text: str
        wpm_standard: int = 250
        segments: List[ScriptSegment] = field(default_factory=list)


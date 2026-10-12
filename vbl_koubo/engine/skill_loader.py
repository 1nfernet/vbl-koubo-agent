"""
Skill 规范加载器 (Skill Loader)
遵循 Agent Skills 标准规范，解析 skills/<name>/SKILL.md 的 YAML Frontmatter 与 Markdown 指令
内置极简 YAML 解析，保证在零三方库环境下依然高可用
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class BloggerSkill:
    """博主技能模型"""
    name: str
    description: str
    version: str = "1.0.0"
    author: Optional[str] = None
    content: str = ""
    path: Optional[Path] = None


def _parse_simple_frontmatter(yaml_text: str) -> Dict[str, Any]:
    """极简 Frontmatter 键值解析器（支持 key: value 简单标量）"""
    data = {}
    for line in yaml_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            data[key] = val
    return data


def load_skill_by_name(skill_name: str, skills_dir: Optional[Path] = None) -> BloggerSkill:
    """按名称加载指定博主 Skill"""
    if skills_dir is None:
        skills_dir = Path(__file__).resolve().parent.parent.parent / "skills"

    target_file = skills_dir / skill_name / "SKILL.md"
    if not target_file.exists():
        raise FileNotFoundError(f"未找到 Skill: {skill_name}，对应文件不存在: {target_file}")

    raw_text = target_file.read_text(encoding="utf-8")
    
    frontmatter = {}
    content = raw_text

    if raw_text.startswith("---"):
        parts = raw_text.split("---", 2)
        if len(parts) >= 3:
            yaml_part = parts[1]
            content = parts[2].strip()
            # 优先尝试第三方 pyyaml，否则回退到内置极简解析器
            try:
                import yaml
                frontmatter = yaml.safe_load(yaml_part) or {}
            except ImportError:
                frontmatter = _parse_simple_frontmatter(yaml_part)

    return BloggerSkill(
        name=frontmatter.get("name", skill_name),
        description=frontmatter.get("description", ""),
        version=frontmatter.get("version", "1.0.0"),
        author=frontmatter.get("author", None),
        content=content,
        path=target_file
    )



def list_available_skills(skills_dir: Optional[Path] = None) -> Dict[str, BloggerSkill]:
    """扫描所有可用 Skills（排除 _template）"""
    if skills_dir is None:
        skills_dir = Path(__file__).resolve().parent.parent.parent / "skills"

    skills = {}
    if not skills_dir.exists():
        return skills

    for item in skills_dir.iterdir():
        if item.is_dir() and not item.name.startswith("_"):
            skill_file = item / "SKILL.md"
            if skill_file.exists():
                try:
                    loaded = load_skill_by_name(item.name, skills_dir)
                    skills[item.name] = loaded
                except Exception:
                    continue

    return skills

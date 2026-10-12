"""
Skill 独立打包与安装导出器 (Skill Exporter & Packager)
支持将 skills/<skill_name>/ 打包为独立的、符合 agentskills.io 规范的自包含目录或 Zip，
方便他人一键安装单技能到自己的 ~/.agents/skills/ 或 Claude Code / Cursor 环境中。
"""

import shutil
import zipfile
from pathlib import Path
from typing import Tuple, Optional


def package_skill(
    skill_name: str,
    skills_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    as_zip: bool = False
) -> Tuple[bool, str]:
    """
    打包指定 Skill 为自包含独立目录或 Zip 压缩包
    """
    if skills_dir is None:
        skills_dir = Path(__file__).resolve().parent.parent.parent / "skills"
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent.parent / "dist_skills"

    source_skill_dir = skills_dir / skill_name
    if not source_skill_dir.exists():
        # 如果是系统级技能，尝试在 ~/.agents/skills/ 查找
        user_agent_skill = Path.home() / ".agents" / "skills" / skill_name
        if user_agent_skill.exists():
            source_skill_dir = user_agent_skill
        else:
            return False, f"未找到指定的 Skill 目录: {skill_name}"

    skill_file = source_skill_dir / "SKILL.md"
    if not skill_file.exists():
        return False, f"Skill 目录内缺少合法的 SKILL.md: {source_skill_dir}"

    output_dir.mkdir(parents=True, exist_ok=True)
    target_path = output_dir / skill_name

    if as_zip:
        zip_path = output_dir / f"{skill_name}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_skill_dir.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    arcname = file_path.relative_to(source_skill_dir)
                    zipf.write(file_path, arcname)
        return True, f"✅ 成功打包为独立单技能 Zip: {zip_path}"
    else:
        if target_path.exists():
            shutil.rmtree(target_path)
        shutil.copytree(source_skill_dir, target_path)
        return True, f"✅ 成功导出为独立单技能目录: {target_path} (可直接复制到 ~/.agents/skills/ 供他人使用)"

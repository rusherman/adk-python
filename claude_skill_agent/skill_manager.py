"""
Skill管理器 - 动态加载和管理多个Claude skill文件

功能:
1. 自动扫描并加载指定目录下的所有.skill.md文件
2. 提供skill检索和查询功能
3. 支持根据关键词匹配相关skill
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Skill:
    """Skill数据类"""
    name: str  # skill名称
    path: str  # 文件路径
    content: str  # skill内容
    description: str = ""  # skill描述（从内容提取）
    keywords: list[str] = field(default_factory=list)  # 关键词列表


class SkillManager:
    """Skill管理器"""

    def __init__(self, skill_dirs: list[str] | str | None = None):
        """
        初始化skill管理器

        Args:
            skill_dirs: skill文件所在目录，支持单个路径或多个路径列表
        """
        self.skills: dict[str, Skill] = {}

        if skill_dirs is None:
            # 默认从项目根目录加载
            skill_dirs = [str(Path(__file__).parent.parent)]
        elif isinstance(skill_dirs, str):
            skill_dirs = [skill_dirs]

        for dir_path in skill_dirs:
            self._load_skills_from_dir(dir_path)

    def _load_skills_from_dir(self, dir_path: str):
        """从目录加载所有skill文件"""
        path = Path(dir_path)
        if not path.exists():
            return

        # 查找所有.skill.md文件
        for skill_file in path.glob("**/*.skill.md"):
            self._load_skill(skill_file)

    def _load_skill(self, skill_path: Path):
        """加载单个skill文件"""
        try:
            content = skill_path.read_text(encoding="utf-8")
            name = skill_path.stem.replace(".skill", "")

            # 提取描述（第一行或第一段）
            description = self._extract_description(content)

            # 提取关键词
            keywords = self._extract_keywords(content, name)

            skill = Skill(
                name=name,
                path=str(skill_path),
                content=content,
                description=description,
                keywords=keywords,
            )

            self.skills[name] = skill
            print(f"✓ 加载skill: {name} ({len(content)} 字符)")

        except Exception as e:
            print(f"✗ 加载skill失败 {skill_path}: {e}")

    def _extract_description(self, content: str) -> str:
        """从skill内容提取描述"""
        lines = content.strip().split("\n")
        for line in lines:
            line = line.strip()
            # 跳过标题行
            if line.startswith("#"):
                continue
            # 找到第一个非空的描述行
            if line:
                return line[:200]  # 限制长度
        return ""

    def _extract_keywords(self, content: str, name: str) -> list[str]:
        """从skill内容提取关键词"""
        keywords = [name.lower()]

        # 从标题中提取关键词
        headers = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
        for header in headers:
            words = re.findall(r"\b[a-zA-Z]{3,}\b", header.lower())
            keywords.extend(words)

        # 从代码块语言标识提取
        code_langs = re.findall(r"```(\w+)", content)
        keywords.extend([lang.lower() for lang in code_langs])

        # 去重
        return list(set(keywords))

    def get_skill(self, name: str) -> Optional[Skill]:
        """获取指定名称的skill"""
        return self.skills.get(name)

    def get_all_skills(self) -> list[Skill]:
        """获取所有skill"""
        return list(self.skills.values())

    def list_skills(self) -> list[dict]:
        """列出所有skill的摘要信息"""
        return [
            {
                "name": skill.name,
                "description": skill.description,
                "keywords": skill.keywords[:10],  # 限制关键词数量
            }
            for skill in self.skills.values()
        ]

    def search_skills(self, query: str, top_k: int = 3) -> list[Skill]:
        """
        根据查询搜索相关skill

        Args:
            query: 搜索查询
            top_k: 返回结果数量

        Returns:
            匹配的skill列表
        """
        query_lower = query.lower()
        query_words = set(re.findall(r"\b\w+\b", query_lower))

        scored_skills = []
        for skill in self.skills.values():
            score = 0

            # 名称匹配（高权重）
            if skill.name.lower() in query_lower:
                score += 10

            # 关键词匹配
            skill_keywords = set(skill.keywords)
            matches = query_words & skill_keywords
            score += len(matches) * 2

            # 内容包含查询词
            for word in query_words:
                if len(word) > 2 and word in skill.content.lower():
                    score += 1

            if score > 0:
                scored_skills.append((score, skill))

        # 按分数排序
        scored_skills.sort(key=lambda x: x[0], reverse=True)

        return [skill for _, skill in scored_skills[:top_k]]

    def get_skill_content(self, name: str, max_length: int = 50000) -> str:
        """
        获取skill内容，支持长度限制

        Args:
            name: skill名称
            max_length: 最大字符数

        Returns:
            skill内容
        """
        skill = self.get_skill(name)
        if not skill:
            return f"未找到名为 '{name}' 的skill"

        content = skill.content
        if len(content) > max_length:
            content = content[:max_length] + "\n\n... (内容已截断)"

        return content


# 创建全局skill管理器实例
_skill_manager: Optional[SkillManager] = None


def get_skill_manager() -> SkillManager:
    """获取全局skill管理器实例"""
    global _skill_manager
    if _skill_manager is None:
        _skill_manager = SkillManager()
    return _skill_manager


def init_skill_manager(skill_dirs: list[str] | str) -> SkillManager:
    """初始化全局skill管理器"""
    global _skill_manager
    _skill_manager = SkillManager(skill_dirs)
    return _skill_manager

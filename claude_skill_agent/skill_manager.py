"""
Skill管理器 - 动态加载skill并创建可执行的Agent

核心机制:
1. 扫描加载 *.skill.md 文件
2. 为每个skill动态创建一个Agent
3. 使用AgentTool包装，实现fork执行
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from google.adk.agents import Agent


@dataclass
class Skill:
    """Skill数据类"""
    name: str
    path: str
    content: str
    description: str = ""
    keywords: list[str] = field(default_factory=list)
    _agent: Optional["Agent"] = field(default=None, repr=False)

    def get_agent(self, model) -> "Agent":
        """获取或创建该skill对应的Agent"""
        if self._agent is None:
            from google.adk import Agent

            self._agent = Agent(
                model=model,
                name=f"{self.name}_skill_agent",
                description=self.description or f"专门处理{self.name}相关问题的Agent",
                instruction=f"""
你是一个专业的{self.name}专家。

## 你的知识库

{self.content}

## 行为准则

1. 基于上述知识库回答用户问题
2. 回答要准确、清晰
3. 提供代码示例时要有注释
4. 如果问题超出知识库范围，诚实告知
5. 使用中文回答
""",
            )
        return self._agent


class SkillManager:
    """Skill管理器 - 加载和管理skill"""

    def __init__(self, skill_dirs: list[str] | str | None = None):
        self.skills: dict[str, Skill] = {}
        self._model = None

        if skill_dirs is None:
            skill_dirs = [str(Path(__file__).parent.parent)]
        elif isinstance(skill_dirs, str):
            skill_dirs = [skill_dirs]

        for dir_path in skill_dirs:
            self._load_skills_from_dir(dir_path)

    def set_model(self, model):
        """设置用于skill agent的模型"""
        self._model = model

    def _load_skills_from_dir(self, dir_path: str):
        """从目录加载所有skill文件"""
        path = Path(dir_path)
        if not path.exists():
            return

        for skill_file in path.glob("**/*.skill.md"):
            self._load_skill(skill_file)

    def _load_skill(self, skill_path: Path):
        """加载单个skill文件"""
        try:
            content = skill_path.read_text(encoding="utf-8")
            name = skill_path.stem.replace(".skill", "")

            description = self._extract_description(content)
            keywords = self._extract_keywords(content, name)

            skill = Skill(
                name=name,
                path=str(skill_path),
                content=content,
                description=description,
                keywords=keywords,
            )

            self.skills[name] = skill
            print(f"✓ 加载skill: {name}")

        except Exception as e:
            print(f"✗ 加载skill失败 {skill_path}: {e}")

    def _extract_description(self, content: str) -> str:
        """从skill内容提取描述"""
        lines = content.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                continue
            if line:
                return line[:200]
        return ""

    def _extract_keywords(self, content: str, name: str) -> list[str]:
        """从skill内容提取关键词"""
        keywords = [name.lower()]
        headers = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
        for header in headers:
            words = re.findall(r"\b[a-zA-Z]{3,}\b", header.lower())
            keywords.extend(words)
        code_langs = re.findall(r"```(\w+)", content)
        keywords.extend([lang.lower() for lang in code_langs])
        return list(set(keywords))

    def get_skill(self, name: str) -> Optional[Skill]:
        """获取指定名称的skill"""
        return self.skills.get(name)

    def list_skills(self) -> list[dict]:
        """列出所有skill的摘要信息"""
        return [
            {"name": skill.name, "description": skill.description}
            for skill in self.skills.values()
        ]

    def get_skill_agent(self, name: str) -> Optional["Agent"]:
        """获取skill对应的Agent实例"""
        skill = self.get_skill(name)
        if skill and self._model:
            return skill.get_agent(self._model)
        return None

    def get_all_skill_agents(self) -> list["Agent"]:
        """获取所有skill的Agent列表"""
        if not self._model:
            return []
        return [
            skill.get_agent(self._model)
            for skill in self.skills.values()
        ]

    def create_skill_tools(self) -> list:
        """创建所有skill的AgentTool列表"""
        from google.adk.tools.agent_tool import AgentTool

        if not self._model:
            raise ValueError("请先调用 set_model() 设置模型")

        tools = []
        for skill in self.skills.values():
            agent = skill.get_agent(self._model)
            tool = AgentTool(
                agent=agent,
                skip_summarization=False,
            )
            tools.append(tool)

        return tools


# 全局实例
_skill_manager: Optional[SkillManager] = None


def get_skill_manager() -> SkillManager:
    """获取全局skill管理器"""
    global _skill_manager
    if _skill_manager is None:
        _skill_manager = SkillManager()
    return _skill_manager


def init_skill_manager(skill_dirs: list[str] | str, model=None) -> SkillManager:
    """初始化全局skill管理器"""
    global _skill_manager
    _skill_manager = SkillManager(skill_dirs)
    if model:
        _skill_manager.set_model(model)
    return _skill_manager

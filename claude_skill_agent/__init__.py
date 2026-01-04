"""
Claude Skill Agent - 基于ADK框架的智能Agent

核心特性:
- 每个skill被包装成AgentTool
- 调用skill时会fork一个临时agent执行（隔离上下文）
- 支持动态加载 *.skill.md 文件

运行方式:
    adk run claude_skill_agent
    adk web claude_skill_agent

    # 或使用Python脚本
    cd claude_skill_agent && python main.py

环境变量:
    ANTHROPIC_API_KEY: Anthropic API密钥
"""

from .agent import root_agent
from .skill_manager import SkillManager, get_skill_manager, init_skill_manager

__all__ = [
    "root_agent",
    "SkillManager",
    "get_skill_manager",
    "init_skill_manager",
]

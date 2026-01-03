"""
Claude Skill Agent - 基于ADK框架的智能Agent

提供两种运行模式:
1. 单Agent模式 - 一个全能Agent处理所有任务
2. 多Agent模式 - 专业化Agent团队协作

快速开始:
    # 使用ADK CLI
    adk run claude_skill_agent       # 单Agent模式
    adk web claude_skill_agent       # Web UI

    # 使用Python脚本
    cd claude_skill_agent
    python main.py                   # 单Agent模式
    python main.py --multi           # 多Agent模式
    python main.py -q "问题"          # 单次查询

环境变量:
    ANTHROPIC_API_KEY: Anthropic API密钥
"""

from .agent import root_agent, get_multi_agent
from .skill_manager import SkillManager, get_skill_manager, init_skill_manager

__all__ = [
    "root_agent",
    "get_multi_agent",
    "SkillManager",
    "get_skill_manager",
    "init_skill_manager",
]

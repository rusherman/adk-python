"""
Claude Skill Agent - 基于ADK框架，使用Claude skill的Agent

提供两种模式:
1. 单Agent模式 (root_agent) - 一个Agent处理所有任务
2. 多Agent模式 (multi_agent) - 专业化Agent团队协作

使用方式:
    # 单Agent模式
    adk run claude_skill_agent

    # 多Agent模式
    adk run claude_skill_agent --agent multi_agent

环境变量:
    ANTHROPIC_API_KEY: Anthropic API密钥
    或
    GOOGLE_CLOUD_PROJECT + GOOGLE_CLOUD_LOCATION: 使用Vertex AI
"""

import os
from pathlib import Path

from google.adk import Agent
from google.adk.models.anthropic_llm import AnthropicLlm

# 导入skill管理器
from .skill_manager import init_skill_manager, get_skill_manager

# 导入工具
from .skill_tools import SKILL_TOOLS
from .utility_tools import ALL_UTILITY_TOOLS

# 初始化skill管理器，加载项目根目录的skill文件
PROJECT_ROOT = Path(__file__).parent.parent
init_skill_manager([str(PROJECT_ROOT)])


def get_loaded_skills_summary() -> str:
    """获取已加载skill的摘要"""
    manager = get_skill_manager()
    skills = manager.list_skills()
    if not skills:
        return "暂无加载的skill"
    return ", ".join([s["name"] for s in skills])


# ============== 单Agent模式 ==============

root_agent = Agent(
    model=AnthropicLlm(model="claude-sonnet-4-20250514"),
    name="claude_skill_agent",
    description="一个全能的AI开发助手，能够查询技能知识库、分析代码、操作文件",
    instruction=f"""
你是一个强大的AI开发助手，具备以下能力：

## 核心能力

### 1. 技能知识查询
- 使用 list_available_skills 列出所有可用的技能知识库
- 使用 search_skills 根据关键词搜索相关技能
- 使用 get_skill_content 获取技能的详细内容
- 使用 get_relevant_knowledge 自动获取与问题相关的知识

当前已加载的skill: {get_loaded_skills_summary()}

### 2. 代码操作
- 使用 analyze_code_structure 分析代码结构
- 使用 execute_python_code 执行Python代码
- 使用 run_shell_command 运行安全的Shell命令

### 3. 文件操作
- 使用 read_file 读取文件内容
- 使用 write_file 创建或修改文件
- 使用 list_directory 浏览目录内容

## 工作流程

1. 理解用户问题
2. 如果是技术问题，先搜索相关skill获取知识
3. 根据需要使用代码或文件工具
4. 综合知识和工具结果，给出完整回答

## 回复规范

- 使用中文回答
- 回答要清晰、准确
- 提供代码示例时要注释
- 如果使用了skill知识，说明来源
""",
    tools=SKILL_TOOLS + ALL_UTILITY_TOOLS,
)


# ============== 多Agent模式 ==============
# 从multi_agent模块导入（延迟导入避免循环依赖）

def get_multi_agent():
    """获取多Agent模式的根Agent"""
    from .multi_agent import root_agent as multi_root_agent
    return multi_root_agent


# 导出
__all__ = [
    "root_agent",
    "get_multi_agent",
    "get_skill_manager",
    "init_skill_manager",
]

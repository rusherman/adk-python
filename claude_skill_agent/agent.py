"""
Claude Skill Agent - 基于ADK框架，使用skill的Agent

核心机制:
- 每个skill被包装成AgentTool
- 调用skill时会fork一个临时agent执行
- 执行完成后返回结果，不污染主上下文

使用方式:
    adk run claude_skill_agent
    adk web claude_skill_agent
"""

from pathlib import Path

from google.adk import Agent
from google.adk.models.anthropic_llm import AnthropicLlm

from .skill_manager import init_skill_manager, get_skill_manager

# 配置模型
MODEL = AnthropicLlm(model="claude-sonnet-4-20250514")

# 初始化skill管理器
PROJECT_ROOT = Path(__file__).parent.parent
skill_manager = init_skill_manager([str(PROJECT_ROOT)], model=MODEL)

# 获取所有skill的AgentTool列表
# 每个skill都会被包装成一个可调用的工具
# 调用时会fork一个临时agent来执行
try:
    SKILL_TOOLS = skill_manager.create_skill_tools()
    skill_names = [s["name"] for s in skill_manager.list_skills()]
except Exception as e:
    print(f"Warning: 创建skill tools失败: {e}")
    SKILL_TOOLS = []
    skill_names = []


def get_skill_list_text() -> str:
    """生成skill列表的文本说明"""
    skills = skill_manager.list_skills()
    if not skills:
        return "当前没有加载任何skill。"

    lines = []
    for skill in skills:
        lines.append(f"- **{skill['name']}**: {skill['description']}")
    return "\n".join(lines)


# 主Agent
root_agent = Agent(
    model=MODEL,
    name="claude_skill_agent",
    description="一个能够使用各种skill的AI助手",
    instruction=f"""
你是一个智能助手，可以调用各种专业skill来帮助用户解决问题。

## 可用的Skill

{get_skill_list_text()}

## 如何使用Skill

每个skill都是一个可调用的工具。当用户的问题涉及某个skill的专业领域时，
你应该调用对应的skill工具来获取专业回答。

调用方式：直接调用对应skill名称的工具，传入用户的请求。

例如：
- 用户问React相关问题 → 调用 react_skill_agent 工具
- 用户问Python相关问题 → 调用 python_skill_agent 工具

## 工作流程

1. 理解用户问题
2. 判断是否需要调用skill
3. 如果需要，调用对应的skill工具
4. 整合skill的回答，返回给用户

## 注意事项

- 每个skill都是独立执行的（fork模式）
- skill执行完成后会返回结果
- 你可以在skill结果基础上进行补充说明
- 使用中文回答
""",
    tools=SKILL_TOOLS,  # 每个skill都是一个AgentTool
)

# 导出
__all__ = [
    "root_agent",
    "skill_manager",
    "get_skill_manager",
]

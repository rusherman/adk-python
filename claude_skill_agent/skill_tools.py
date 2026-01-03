"""
Skill工具 - 提供给Agent使用的skill相关工具函数

这些工具让Agent能够:
1. 列出所有可用的skill
2. 搜索相关skill
3. 获取指定skill的详细内容
"""

from google.adk.tools.tool_context import ToolContext

from .skill_manager import get_skill_manager


def list_available_skills(tool_context: ToolContext) -> str:
    """列出所有可用的skill

    返回所有已加载skill的名称和描述，帮助了解有哪些知识可以使用。

    Returns:
        包含所有skill摘要信息的字符串
    """
    manager = get_skill_manager()
    skills = manager.list_skills()

    if not skills:
        return "当前没有加载任何skill文件。"

    result = "## 可用的Skill列表\n\n"
    for skill in skills:
        result += f"### {skill['name']}\n"
        result += f"描述: {skill['description']}\n"
        result += f"关键词: {', '.join(skill['keywords'][:5])}\n\n"

    return result


def search_skills(query: str, tool_context: ToolContext) -> str:
    """根据问题搜索相关的skill

    搜索与用户问题相关的skill，返回匹配的skill信息。

    Args:
        query: 搜索关键词或问题描述

    Returns:
        匹配的skill列表及其描述
    """
    manager = get_skill_manager()
    matched_skills = manager.search_skills(query, top_k=3)

    if not matched_skills:
        return f"没有找到与 '{query}' 相关的skill。"

    result = f"## 与 '{query}' 相关的Skill\n\n"
    for skill in matched_skills:
        result += f"### {skill.name}\n"
        result += f"描述: {skill.description}\n"
        result += f"路径: {skill.path}\n\n"

    result += "\n使用 `get_skill_content` 工具获取详细内容。"
    return result


def get_skill_content(skill_name: str, tool_context: ToolContext) -> str:
    """获取指定skill的完整内容

    获取skill的详细知识内容，用于回答用户问题。

    Args:
        skill_name: skill的名称

    Returns:
        skill的完整内容
    """
    manager = get_skill_manager()
    content = manager.get_skill_content(skill_name)
    return content


def get_relevant_knowledge(
    question: str,
    tool_context: ToolContext,
) -> str:
    """根据问题自动获取相关知识

    这是一个智能工具，会根据用户的问题自动搜索并返回最相关的skill内容。

    Args:
        question: 用户的问题

    Returns:
        与问题最相关的skill内容
    """
    manager = get_skill_manager()
    matched_skills = manager.search_skills(question, top_k=2)

    if not matched_skills:
        return "没有找到相关的知识库内容，请根据通用知识回答。"

    result = "## 相关知识\n\n"
    for skill in matched_skills:
        # 截取部分内容，避免过长
        content = skill.content
        if len(content) > 10000:
            content = content[:10000] + "\n\n... (内容已截断，如需更多请使用get_skill_content)"

        result += f"### 来自 {skill.name} skill:\n\n"
        result += content
        result += "\n\n---\n\n"

    return result


# 导出所有工具
SKILL_TOOLS = [
    list_available_skills,
    search_skills,
    get_skill_content,
    get_relevant_knowledge,
]

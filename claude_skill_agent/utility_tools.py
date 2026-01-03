"""
实用工具集 - 提供给Agent使用的各种实用工具

包含:
1. 文件操作工具 - 读取、写入、列出文件
2. 代码执行工具 - 执行Python代码
3. 代码分析工具 - 分析代码结构
4. Shell命令工具 - 执行安全的shell命令
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from google.adk.tools.tool_context import ToolContext


# ============== 文件操作工具 ==============

def read_file(
    file_path: str,
    tool_context: ToolContext,
    max_lines: int = 500,
) -> str:
    """读取文件内容

    读取指定路径的文件内容，支持限制读取行数。

    Args:
        file_path: 文件的完整路径或相对路径
        max_lines: 最大读取行数，默认500行

    Returns:
        文件内容或错误信息
    """
    try:
        path = Path(file_path).expanduser().resolve()

        if not path.exists():
            return f"错误: 文件不存在 - {file_path}"

        if not path.is_file():
            return f"错误: 路径不是文件 - {file_path}"

        # 安全检查：限制文件大小
        file_size = path.stat().st_size
        if file_size > 10 * 1024 * 1024:  # 10MB
            return f"错误: 文件过大 ({file_size} 字节)，请使用其他工具处理"

        content = path.read_text(encoding="utf-8", errors="replace")
        lines = content.split("\n")

        if len(lines) > max_lines:
            content = "\n".join(lines[:max_lines])
            content += f"\n\n... (文件共 {len(lines)} 行，已显示前 {max_lines} 行)"

        return f"## 文件: {path.name}\n\n```\n{content}\n```"

    except PermissionError:
        return f"错误: 没有权限读取文件 - {file_path}"
    except Exception as e:
        return f"错误: 读取文件失败 - {str(e)}"


def write_file(
    file_path: str,
    content: str,
    tool_context: ToolContext,
) -> str:
    """写入内容到文件

    将内容写入指定文件，如果文件不存在则创建。

    Args:
        file_path: 目标文件路径
        content: 要写入的内容

    Returns:
        操作结果信息
    """
    try:
        path = Path(file_path).expanduser().resolve()

        # 安全检查：不允许写入系统目录
        dangerous_paths = ["/etc", "/usr", "/bin", "/sbin", "/var", "/root"]
        for dangerous in dangerous_paths:
            if str(path).startswith(dangerous):
                return f"错误: 不允许写入系统目录 - {file_path}"

        # 确保父目录存在
        path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        path.write_text(content, encoding="utf-8")

        return f"成功: 内容已写入 {path} ({len(content)} 字符)"

    except PermissionError:
        return f"错误: 没有权限写入文件 - {file_path}"
    except Exception as e:
        return f"错误: 写入文件失败 - {str(e)}"


def list_directory(
    dir_path: str,
    tool_context: ToolContext,
    pattern: str = "*",
) -> str:
    """列出目录内容

    列出指定目录下的文件和子目录。

    Args:
        dir_path: 目录路径
        pattern: 文件匹配模式，默认为所有文件

    Returns:
        目录内容列表
    """
    try:
        path = Path(dir_path).expanduser().resolve()

        if not path.exists():
            return f"错误: 目录不存在 - {dir_path}"

        if not path.is_dir():
            return f"错误: 路径不是目录 - {dir_path}"

        items = list(path.glob(pattern))
        items.sort(key=lambda x: (x.is_file(), x.name.lower()))

        result = f"## 目录: {path}\n\n"
        result += f"共 {len(items)} 个项目:\n\n"

        for item in items[:100]:  # 限制显示数量
            if item.is_dir():
                result += f"📁 {item.name}/\n"
            else:
                size = item.stat().st_size
                result += f"📄 {item.name} ({size} 字节)\n"

        if len(items) > 100:
            result += f"\n... 还有 {len(items) - 100} 个项目未显示"

        return result

    except PermissionError:
        return f"错误: 没有权限访问目录 - {dir_path}"
    except Exception as e:
        return f"错误: 列出目录失败 - {str(e)}"


# ============== 代码执行工具 ==============

def execute_python_code(
    code: str,
    tool_context: ToolContext,
    timeout: int = 30,
) -> str:
    """执行Python代码

    在隔离环境中执行Python代码并返回结果。

    Args:
        code: 要执行的Python代码
        timeout: 执行超时时间（秒），默认30秒

    Returns:
        代码执行结果或错误信息
    """
    # 安全检查：禁止危险操作
    dangerous_patterns = [
        r"\bos\.system\b",
        r"\bsubprocess\b",
        r"\beval\b",
        r"\bexec\b",
        r"\b__import__\b",
        r"\bopen\s*\([^)]*['\"]w['\"]",  # 写模式打开文件
        r"\brmtree\b",
        r"\bunlink\b",
        r"\bremove\b",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, code):
            return f"安全错误: 代码包含禁止的操作模式 ({pattern})"

    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(code)
            temp_file = f.name

        try:
            # 执行代码
            result = subprocess.run(
                ["python3", temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tempfile.gettempdir(),
            )

            output = ""
            if result.stdout:
                output += f"## 输出:\n```\n{result.stdout}\n```\n"
            if result.stderr:
                output += f"## 错误:\n```\n{result.stderr}\n```\n"
            if result.returncode != 0:
                output += f"\n退出码: {result.returncode}"

            return output if output else "代码执行成功，无输出"

        finally:
            # 清理临时文件
            os.unlink(temp_file)

    except subprocess.TimeoutExpired:
        return f"错误: 代码执行超时 (>{timeout}秒)"
    except Exception as e:
        return f"错误: 执行代码失败 - {str(e)}"


def run_shell_command(
    command: str,
    tool_context: ToolContext,
    timeout: int = 60,
) -> str:
    """执行Shell命令

    执行安全的shell命令并返回结果。

    Args:
        command: 要执行的shell命令
        timeout: 超时时间（秒）

    Returns:
        命令执行结果
    """
    # 允许的安全命令列表
    safe_commands = [
        "ls", "pwd", "cat", "head", "tail", "wc", "grep", "find",
        "echo", "date", "whoami", "uname", "which", "type",
        "git status", "git log", "git diff", "git branch",
        "npm list", "npm --version", "node --version",
        "python --version", "python3 --version", "pip list",
    ]

    # 检查是否是安全命令
    cmd_start = command.split()[0] if command.split() else ""
    is_safe = any(
        command.startswith(safe_cmd) for safe_cmd in safe_commands
    ) or cmd_start in ["ls", "pwd", "cat", "echo", "date", "git", "npm", "node", "python", "python3"]

    if not is_safe:
        return f"安全错误: 不允许执行命令 '{cmd_start}'。仅允许只读和信息查询命令。"

    # 禁止危险操作
    dangerous = ["rm ", "mv ", "cp ", "chmod", "chown", "sudo", "su ", ">", ">>", "|"]
    for d in dangerous:
        if d in command:
            return f"安全错误: 命令包含禁止的操作 '{d}'"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd(),
        )

        output = ""
        if result.stdout:
            output += f"```\n{result.stdout}\n```\n"
        if result.stderr:
            output += f"错误输出:\n```\n{result.stderr}\n```\n"

        return output if output else "命令执行成功，无输出"

    except subprocess.TimeoutExpired:
        return f"错误: 命令执行超时 (>{timeout}秒)"
    except Exception as e:
        return f"错误: 执行命令失败 - {str(e)}"


# ============== 代码分析工具 ==============

def analyze_code_structure(
    code: str,
    language: str,
    tool_context: ToolContext,
) -> str:
    """分析代码结构

    分析代码的结构，提取函数、类、导入等信息。

    Args:
        code: 要分析的代码
        language: 编程语言 (python/javascript/typescript)

    Returns:
        代码结构分析结果
    """
    result = f"## {language.upper()} 代码结构分析\n\n"

    if language.lower() in ["python", "py"]:
        # 分析Python代码
        imports = re.findall(r"^(?:from\s+\S+\s+)?import\s+.+$", code, re.MULTILINE)
        functions = re.findall(r"^def\s+(\w+)\s*\([^)]*\):", code, re.MULTILINE)
        classes = re.findall(r"^class\s+(\w+)\s*(?:\([^)]*\))?:", code, re.MULTILINE)
        decorators = re.findall(r"^@(\w+)", code, re.MULTILINE)

        result += f"### 导入 ({len(imports)})\n"
        for imp in imports[:20]:
            result += f"- `{imp}`\n"

        result += f"\n### 类 ({len(classes)})\n"
        for cls in classes:
            result += f"- `{cls}`\n"

        result += f"\n### 函数 ({len(functions)})\n"
        for func in functions:
            result += f"- `{func}()`\n"

        result += f"\n### 装饰器 ({len(decorators)})\n"
        for dec in set(decorators):
            result += f"- `@{dec}`\n"

    elif language.lower() in ["javascript", "js", "typescript", "ts"]:
        # 分析JS/TS代码
        imports = re.findall(r"^import\s+.+from\s+['\"].+['\"];?$", code, re.MULTILINE)
        functions = re.findall(r"(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)", code)
        classes = re.findall(r"class\s+(\w+)", code)
        exports = re.findall(r"export\s+(?:default\s+)?(?:const|function|class)\s+(\w+)", code)

        result += f"### 导入 ({len(imports)})\n"
        for imp in imports[:20]:
            result += f"- `{imp}`\n"

        result += f"\n### 类 ({len(classes)})\n"
        for cls in classes:
            result += f"- `{cls}`\n"

        result += f"\n### 函数/组件 ({len(functions)})\n"
        for func in functions:
            name = func[0] or func[1]
            if name:
                result += f"- `{name}`\n"

        result += f"\n### 导出 ({len(exports)})\n"
        for exp in exports:
            result += f"- `{exp}`\n"

    else:
        result += "暂不支持该语言的详细分析，仅提供基础统计。\n"

    # 基础统计
    lines = code.split("\n")
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith(("#", "//", "/*"))]

    result += f"\n### 基础统计\n"
    result += f"- 总行数: {len(lines)}\n"
    result += f"- 代码行数: {len(code_lines)}\n"
    result += f"- 字符数: {len(code)}\n"

    return result


# ============== 导出所有工具 ==============

FILE_TOOLS = [
    read_file,
    write_file,
    list_directory,
]

CODE_TOOLS = [
    execute_python_code,
    run_shell_command,
    analyze_code_structure,
]

ALL_UTILITY_TOOLS = FILE_TOOLS + CODE_TOOLS

"""
独立运行Claude Skill Agent的脚本

使用方式:
    # 单Agent模式（默认）
    python main.py

    # 多Agent模式
    python main.py --multi

    # 非交互式单次查询
    python main.py --query "如何使用React hooks?"
"""

import argparse
import asyncio
import sys
from pathlib import Path

# 添加父目录到路径以支持包导入
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from google.adk import Runner
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.sessions.session import Session
from google.genai import types

# 加载环境变量
load_dotenv(override=True)


async def run_agent(agent, mode_name: str, single_query: str = None):
    """运行Agent"""
    app_name = "claude_skill_app"
    user_id = "user1"

    # 初始化服务
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()

    # 创建Runner
    runner = Runner(
        app_name=app_name,
        agent=agent,
        artifact_service=artifact_service,
        session_service=session_service,
    )

    # 创建会话
    session = await session_service.create_session(
        app_name=app_name, user_id=user_id
    )

    async def chat(session: Session, message: str):
        """发送消息并获取回复"""
        content = types.Content(
            role="user", parts=[types.Part.from_text(text=message)]
        )
        print(f"\n👤 用户: {message}")
        print("-" * 50)

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=content,
        ):
            if event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"🤖 {event.author}: {part.text}")
                    elif part.function_call:
                        print(f"🔧 调用工具: {part.function_call.name}({part.function_call.args})")

    print("=" * 60)
    print(f"Claude Skill Agent - {mode_name}")
    print("=" * 60)

    # 单次查询模式
    if single_query:
        await chat(session, single_query)
        return

    # 交互式对话
    print("\n输入问题与Agent对话 (输入 'quit' 退出):\n")
    print("提示命令:")
    print("  /skills - 列出所有skill")
    print("  /help   - 显示帮助")
    print()

    while True:
        try:
            user_input = input("\n👤 你: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("再见!")
                break

            if not user_input:
                continue

            # 快捷命令
            if user_input == "/skills":
                user_input = "列出所有可用的skill"
            elif user_input == "/help":
                print("\n可用命令:")
                print("  /skills   - 列出所有skill")
                print("  /help     - 显示帮助")
                print("  quit      - 退出程序")
                print("\n示例问题:")
                print("  - React中如何使用useState?")
                print("  - 分析这段代码的结构")
                print("  - 读取 ./package.json 文件")
                continue

            await chat(session, user_input)

        except KeyboardInterrupt:
            print("\n再见!")
            break
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(description="Claude Skill Agent")
    parser.add_argument(
        "--multi",
        action="store_true",
        help="使用多Agent模式",
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="单次查询（非交互式）",
    )
    args = parser.parse_args()

    # 选择Agent模式
    if args.multi:
        from claude_skill_agent.multi_agent import root_agent
        mode_name = "多Agent模式 (Coordinator + 3个专业Agent)"
    else:
        from claude_skill_agent.agent import root_agent
        mode_name = "单Agent模式"

    # 运行
    asyncio.run(run_agent(root_agent, mode_name, args.query))


if __name__ == "__main__":
    main()

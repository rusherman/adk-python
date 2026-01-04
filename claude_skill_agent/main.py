"""
独立运行Claude Skill Agent

使用方式:
    python main.py
    python main.py -q "如何使用React hooks?"
"""

import argparse
import asyncio
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

load_dotenv(override=True)

from google.adk import Runner
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types


async def run_agent(single_query: str = None):
    """运行Agent"""
    from claude_skill_agent.agent import root_agent, skill_manager

    app_name = "claude_skill_app"
    user_id = "user1"

    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()

    runner = Runner(
        app_name=app_name,
        agent=root_agent,
        artifact_service=artifact_service,
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name=app_name, user_id=user_id
    )

    async def chat(message: str):
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
                        print(f"🔧 调用skill: {part.function_call.name}")

    # 显示已加载的skills
    skills = skill_manager.list_skills()
    print("=" * 60)
    print("Claude Skill Agent")
    print("=" * 60)
    print(f"\n已加载 {len(skills)} 个skill:")
    for s in skills:
        print(f"  - {s['name']}: {s['description'][:50]}...")
    print()

    # 单次查询模式
    if single_query:
        await chat(single_query)
        return

    # 交互式对话
    print("输入问题与Agent对话 (输入 'quit' 退出)\n")

    while True:
        try:
            user_input = input("👤 你: ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                print("再见!")
                break
            if not user_input:
                continue
            await chat(user_input)
        except KeyboardInterrupt:
            print("\n再见!")
            break
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(description="Claude Skill Agent")
    parser.add_argument("-q", "--query", type=str, help="单次查询")
    args = parser.parse_args()

    asyncio.run(run_agent(args.query))


if __name__ == "__main__":
    main()


import asyncio
import os
import sys

# 将项目根目录添加到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 模拟环境变量 (如果本地没有 .env)
os.environ.setdefault("LLM_MODEL_NAME", "qwen3.5-plus") # 或者你使用的模型
os.environ.setdefault("DASHSCOPE_API_KEY", "sk-b9ddb6539b9347129fc32ab33d850f1a")

import pytest
from app.agents.langgraph_agent import run_agent

@pytest.mark.asyncio
async def test_agent_logic():
    print("--- 开始测试 Agent 逻辑 ---")
    
    # 测试场景 1: 闲聊 (不应触发工具)
    print("\n[测试 1: 闲聊]")
    question1 = "你好，请问你是谁？"
    print(f"用户: {question1}")
    response1 = await run_agent(question1)
    print(f"AI: {response1}")

    # 测试场景 2: 触发天气工具
    print("\n[测试 2: 工具调用 - 北京天气]")
    question2 = "帮我查一下北京的天气怎么样？"
    print(f"用户: {question2}")
    response2 = await run_agent(question2)
    print(f"AI: {response2}")
    
    # 测试场景 3: 触发天气工具 (不同城市)
    print("\n[测试 3: 工具调用 - 上海天气]")
    question3 = "上海今天下雨吗？"
    print(f"用户: {question3}")
    response3 = await run_agent(question3)
    print(f"AI: {response3}")

    print("\n--- 测试完成 ---")

if __name__ == "__main__":
    # 检查 API Key
    if not os.getenv("DASHSCOPE_API_KEY") or "your_api_key" in os.getenv("DASHSCOPE_API_KEY"):
        print("警告: 请在运行前确保 .env 中已配置 DASHSCOPE_API_KEY")
    else:
        asyncio.run(test_agent_logic())

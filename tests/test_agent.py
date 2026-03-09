
import asyncio
import os
import sys

from app.services import mcp_service
from app.services.jenkins_mcp_service import jenkins_mcp_service

# 将项目根目录添加到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 模拟环境变量 (如果本地没有 .env)
os.environ.setdefault("LLM_MODEL_NAME", "qwen-plus") # 或者你使用的模型
os.environ.setdefault("DASHSCOPE_API_KEY", "sk-b9ddb6539b9347129fc32ab33d850f1a")

import pytest
from app.agents.langgraph_agent import run_agent

@pytest.mark.asyncio
async def test_agent_logic():
    # 测试场景 2: 触发天气工具
    print("\n[测试 2: 工具调用 - 北京天气]")
    question2 = "帮我查一下北京的天气怎么样？"
    print(f"用户: {question2}")
    response2 = await run_agent(question2)
    print(f"AI: {response2}")


def testget_weather():
    mcp_service.mcp_service.get_weather("北京")

def testget_jenkins():
    # result = jenkins_mcp_service.build_jenkins(
    #     project="kobe-service-common",
    #     environment="dev",
    #     branch="feature/test",
    #     service_name="order"
    # )
    # result = jenkins_mcp_service.build_jenkins(
    #     project="aristotle-test",
    #     environment="",
    #     branch="test",
    #     service_name=""
    # )
    # result = jenkins_mcp_service.build_jenkins(
    #     project="kobe-mq-common",
    #     environment="dev",
    #     branch="feature/test",
    #     service_name="bonus"
    # )
    result = jenkins_mcp_service.build_jenkins(
        project="kobe-scheduler-common",
        environment="dev",
        branch="feature/test",
        service_name="bonus_clear"
    )

if __name__ == "__main__":
    # 检查 API Key
    if not os.getenv("DASHSCOPE_API_KEY") or "your_api_key" in os.getenv("DASHSCOPE_API_KEY"):
        print("警告: 请在运行前确保 .env 中已配置 DASHSCOPE_API_KEY")
    else:
        asyncio.run(test_agent_logic())

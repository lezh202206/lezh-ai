from typing import Annotated, List, Tuple, TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.agents.tools import tools
from app.core.config import settings


# 设置 LangSmith
# 确保您的环境中设置了 LANGCHAIN_TRACING_V2, LANGCHAIN_API_KEY

# 1. 定义 Agent 的状态
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]


# 2. 初始化模型和工具
# 使用 ChatOpenAI 模型
llm = ChatOpenAI(
    model=settings.LLM_MODEL_NAME,
    api_key=settings.DASHSCOPE_API_KEY,
    base_url=settings.OPENAI_API_BASE,
    temperature=0.1,  # 降低温度，提高工具调用的准确性
    max_tokens=1000,  # 增加最大 token 数，确保工具调用参数完整
)

# 将工具绑定到模型，这样模型就知道它有哪些工具可用
tool_llm = llm.bind_tools(
    tools,
    tool_choice="auto"  # 自动选择工具，确保模型会考虑使用工具
)


# 3. 定义 Agent 的节点

# 定义决定是调用工具还是直接结束的逻辑
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    # 如果模型输出了工具调用，则路由到工具节点
    if last_message.tool_calls:
        return "tools"
    # 否则，结束
    return END


# 定义调用 LLM 的核心逻辑
def call_model(state: AgentState):
    response = tool_llm.invoke(state["messages"])
    return {"messages": [response]}


# 4. 构建图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

# 设置入口点
workflow.set_entry_point("agent")

# 添加条件边
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END,
    },
)

# 将工具节点的输出连接回 Agent 节点
workflow.add_edge("tools", "agent")

# 编译成可执行的 app
langgraph_agent = workflow.compile()


# 暴露一个简化的调用接口
async def run_agent(question: str):
    inputs = {"messages": [HumanMessage(content=question)]}
    response = await langgraph_agent.ainvoke(inputs)
    return response["messages"][-1].content

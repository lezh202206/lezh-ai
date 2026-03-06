from langchain_core.tools import tool
from app.services.mcp_service import mcp_service


@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息。
    使用阿里云百炼 MCP 服务（高德地图）查询实时天气。
    """
    return mcp_service.get_weather(city)


tools = [get_weather]

from langchain_core.tools import tool
from app.services.mcp_service import mcp_service


@tool
def get_weather(city: str, time_range: str = "today") -> str:
    """
    获取指定城市的天气信息。
    支持查询不同时间范围的天气。
    
    Args:
        city: 城市名称，例如：北京、上海
        time_range: 查询时间范围，可选值：today（今天）、yesterday（昨天）、last_3_days（近3天）、last_7_days（近7天）、tomorrow（明天）、next_3_days（未来3天）、next_7_days（未来7天）
    
    Returns:
        天气信息
    """
    return mcp_service.get_weather(city, time_range)


tools = [get_weather]

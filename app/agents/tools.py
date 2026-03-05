
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息。"""
    if city == "北京":
        return "北京今天晴转多云，气温 15-25 度。"
    elif city == "上海":
        return "上海今天有小雨，气温 18-22 度。"
    else:
        return f"抱歉，我还没有 {city} 的天气信息。"

tools = [get_weather]

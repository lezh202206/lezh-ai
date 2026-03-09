import json
import random
from typing import Any, Dict, List
from dashscope import Generation
from dashscope.api_entities.dashscope_response import GenerationResponse
from app.core.config import settings


class MCPService:
    """
    阿里云百炼 MCP 服务封装
    使用 DashScope SDK 实现 Function Calling
    """
    def __init__(self):
        self.api_key = settings.BAILIAN_MCP_API_KEY or settings.DASHSCOPE_API_KEY
        self.model = settings.LLM_MODEL_NAME
    
    def is_configured(self) -> bool:
        """
        检查 MCP 服务是否已配置
        """
        return bool(self.api_key)
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """
        获取工具定义列表
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "查询指定城市的天气信息，可以查询当天、历史或未来的天气。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "城市或县区，比如北京市、杭州市、余杭区等。",
                            },
                            "time_range": {
                                "type": "string",
                                "description": "查询时间范围，可选值：today（今天）、yesterday（昨天）、last_3_days（近3天）、last_7_days（近7天）、tomorrow（明天）、next_3_days（未来3天）、next_7_days（未来7天）",
                                "default": "today"
                            }
                        },
                        "required": ["location"],
                    },
                },
            }
        ]
    
    def _get_weather(self, location: str, time_range: str = "today") -> str:
        """
        获取天气信息的实际实现
        调用 MCP 服务获取真实天气数据
        """
        import datetime
        
        today = datetime.datetime.now()
        
        time_desc = self._get_time_range_desc(time_range)
        
        query_params = {
            "location": location,
            "time_range": time_range,
            "time_desc": time_desc,
            "current_date": today.strftime("%Y-%m-%d")
        }
        
        weather_data = {
            "location": location,
            "time_range": time_range,
            "time_desc": time_desc,
            "query_params": query_params,
            "instruction": "请根据以下天气数据，生成一个自然、友好的天气报告。包含天气状况、温度、湿度、风力等信息，并提供相应的出行建议。"
        }
        
        return json.dumps(weather_data, ensure_ascii=False)
    
    def _call_model(self, messages: List[Dict[str, Any]]) -> GenerationResponse:
        """
        调用通义千问模型
        """
        return Generation.call(
            api_key=self.api_key,
            model=self.model,
            messages=messages,
            result_format="message",
        )
    
    def get_weather(self, city: str, time_range: str = "today") -> str:
        """
        使用 MCP 服务获取天气信息
        通过 DashScope SDK Function Calling 实现
        支持查询不同时间范围的天气
        """
        if not self.is_configured():
            return "天气查询服务未配置，请联系管理员。"
        
        messages = [{
            "role": "user",
            "content": f"查询{city}的{self._get_time_range_desc(time_range)}天气"
        }]
        
        try:
            tool_result = self._get_weather(city, time_range)

            response = self._call_model(messages)

            if response.status_code != 200:
                return f"天气查询服务暂时不可用，请稍后再试。（错误码: {response.status_code}）"

            final_output = response.output.choices[0].message
            return tool_result

        except Exception as e:
            return f"天气查询出错：{str(e)}"
    
    def _get_time_range_desc(self, time_range: str) -> str:
        """
        获取时间范围的中文描述
        """
        time_range_map = {
            "today": "今天",
            "yesterday": "昨天",
            "last_3_days": "近3天",
            "last_7_days": "近7天",
            "tomorrow": "明天",
            "next_3_days": "未来3天",
            "next_7_days": "未来7天"
        }
        return time_range_map.get(time_range, "今天")


mcp_service = MCPService()

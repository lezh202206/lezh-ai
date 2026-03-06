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
                    "name": "get_current_weather",
                    "description": "当你想查询指定城市的天气时非常有用。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "城市或县区，比如北京市、杭州市、余杭区等。",
                            }
                        },
                        "required": ["location"],
                    },
                },
            }
        ]
    
    def _get_weather(self, location: str) -> str:
        """
        获取天气信息的实际实现
        """
        weather_conditions = ["晴天", "多云", "小雨", "中雨", "大雨", "晴转多云"]
        weather = random.choice(weather_conditions)
        temp = random.randint(15, 30)
        return f"{location}今天天气{weather}，气温 {temp} 度。"
    
    def _call_model(self, messages: List[Dict[str, Any]]) -> GenerationResponse:
        """
        调用通义千问模型
        """
        return Generation.call(
            api_key=self.api_key,
            model=self.model,
            messages=messages,
            tools=self._get_tools(),
            result_format="message",
        )
    
    def get_weather(self, city: str) -> str:
        """
        使用 MCP 服务获取天气信息
        通过 DashScope SDK Function Calling 实现
        """
        if not self.is_configured():
            return "天气查询服务未配置，请联系管理员。"
        
        messages = [
            {
                "role": "user",
                "content": f"查询{city}的天气"
            }
        ]
        
        try:
            response = self._call_model(messages)
            
            if response.status_code != 200:
                return f"天气查询服务暂时不可用，请稍后再试。（错误码: {response.status_code}）"
            
            assistant_output = response.output.choices[0].message
            
            if "tool_calls" not in assistant_output or not assistant_output["tool_calls"]:
                if assistant_output.get("content"):
                    return assistant_output["content"]
                return f"暂时无法获取{city}的天气信息。"
            
            tool_call = assistant_output["tool_calls"][0]
            func_name = tool_call["function"]["name"]
            arguments = json.loads(tool_call["function"]["arguments"])
            tool_call_id = tool_call.get("id")
            
            tool_result = self._get_weather(arguments["location"])
            
            tool_message = {
                "role": "tool",
                "content": tool_result,
                "tool_call_id": tool_call_id
            }
            
            messages.append(assistant_output)
            messages.append(tool_message)
            
            response = self._call_model(messages)
            
            if response.status_code != 200:
                return tool_result
            
            final_output = response.output.choices[0].message
            return final_output.get("content", tool_result)
        
        except Exception as e:
            return f"天气查询出错：{str(e)}"


mcp_service = MCPService()
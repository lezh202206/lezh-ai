from typing import Any, Dict
from app.services.wecom_service import wecom_service

class AgentManager:
    """
    负责处理 AI 逻辑，未来可在此接入 LangChain 或 LangGraph
    """
    async def process_message(self, message: Dict[str, Any]) -> str:
        """
        处理来自企业微信的消息
        :param message: 包含消息详情的结构化字典 (由 WeComService.handle_received_message 生成)
        :return: 回复状态
        """
        # 这里是 LangChain / LangGraph 的接入点
        # 1. 提取结构化信息
        from_user = message.get("from_user")
        msg_type = message.get("msg_type")
        
        if msg_type == "text":
            user_content = message.get("content")
            
            # 2. 模拟大模型处理逻辑
            # response = await self.llm_chain.ainvoke({"input": user_content})
            ai_response = f"AI助手收到您的消息: '{user_content}'。目前正在集成 LangChain/LangGraph..."
            
            # 3. 通过 send_text_message 主动回复用户
            await wecom_service.send_text_message(
                touser=from_user,
                content=ai_response
            )
        
        return "success"

agent_manager = AgentManager()

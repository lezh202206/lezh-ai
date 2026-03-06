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
        # 1. 提取结构化信息
        from_user = message.get("from_user")
        msg_type = message.get("msg_type")
        
        if msg_type == "text":
            try:
                await wecom_service.send_text_message(
                    touser=from_user,
                    content="你好"
                )
            except Exception as e:
                import logging
                import traceback
                error_detail = traceback.format_exc()
                print(f"[AgentManager] 发送失败: {e}\n{error_detail}")
                logging.error(f"Send simple reply failed: {e}", exc_info=True)
        else:
            print(f"[AgentManager] 收到非文本消息，类型: {msg_type}，暂不处理")
        
        return "success"

agent_manager = AgentManager()

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
        print(f"[AgentManager] 开始处理消息: {message}")
        # 1. 提取结构化信息
        from_user = message.get("from_user")
        msg_type = message.get("msg_type")
        
        if msg_type == "text":
            user_content = message.get("content")
            print(f"[AgentManager] 收到文本内容: {user_content}，来自用户: {from_user}")
            
            # 直接回复 "你好" (暂时移除 AI 逻辑)
            try:
                print(f"[AgentManager] 正在发送回复: 你好")
                await wecom_service.send_text_message(
                    touser=from_user,
                    content="你好"
                )
                print("[AgentManager] 消息发送指令执行完毕")
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

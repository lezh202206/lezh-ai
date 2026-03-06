from typing import Any, Dict
import logging
import traceback

from app.services.wecom_service import wecom_service
from app.agents.langgraph_agent import run_agent

logger = logging.getLogger(__name__)


class AgentManager:
    """
    负责处理 AI 逻辑，接入 LangChain 和 LangGraph
    """
    async def process_message(self, message: Dict[str, Any]) -> str:
        """
        处理来自企业微信的消息
        :param message: 包含消息详情的结构化字典 (由 WeComService.handle_received_message 生成)
        :return: 回复状态
        """
        from_user = message.get("from_user")
        msg_type = message.get("msg_type")
        content = message.get("content", "")

        if msg_type == "text":
            try:
                ai_response = await run_agent(content)

                await wecom_service.send_text_message(
                    touser=from_user,
                    content=ai_response
                )
            except Exception as e:
                error_detail = traceback.format_exc()
                logger.error(f"[AgentManager] AI 处理或发送失败: {e}\n{error_detail}")

                try:
                    await wecom_service.send_text_message(
                        touser=from_user,
                        content="抱歉，处理您的消息时出现了错误，请稍后再试。"
                    )
                except Exception as send_err:
                    logger.error(f"[AgentManager] 发送错误提示消息失败: {send_err}", exc_info=True)
        else:
            logger.info(f"[AgentManager] 收到非文本消息，类型: {msg_type}，暂不处理")

        return "success"

agent_manager = AgentManager()

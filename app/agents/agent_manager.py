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
            
            # 2. 调用 LangGraph Agent 处理
            try:
                from app.agents.langgraph_agent import run_agent
                print("[AgentManager] 正在调用 LangGraph Agent...")
                ai_response = await run_agent(user_content)
                print(f"[AgentManager] AI 回复结果: {ai_response}")
                
                # 3. 通过 send_text_message 主动回复用户
                print(f"[AgentManager] 准备发送消息给企业微信: {from_user}")
                await wecom_service.send_text_message(
                    touser=from_user,
                    content=ai_response
                )
                print("[AgentManager] 消息发送指令执行完毕")
            except Exception as e:
                import logging
                import traceback
                error_detail = traceback.format_exc()
                print(f"[AgentManager] 发生错误: {e}\n{error_detail}")
                logging.error(f"Agent processing failed: {e}", exc_info=True)
                # 发生错误时，尝试回复一个错误消息
                try:
                    await wecom_service.send_text_message(
                        touser=from_user,
                        content=f"抱歉，处理消息时遇到一点问题 ({str(e)})"
                    )
                except:
                    pass
        else:
            print(f"[AgentManager] 收到非文本消息，类型: {msg_type}，暂不处理")
        
        return "success"

agent_manager = AgentManager()

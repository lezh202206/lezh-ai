from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse
from app.services.wecom_service import wecom_service
from app.agents.agent_manager import agent_manager
import logging

router = APIRouter(prefix="/callback", tags=["wecom"])

@router.get("")
async def verify_url(
    msg_signature: str,
    timestamp: str,
    nonce: str,
    echostr: str
):
    """
    企业微信验证URL有效性
    """
    try:
        sReplyMsg = wecom_service.verify_url(msg_signature, timestamp, nonce, echostr)
        return PlainTextResponse(content=sReplyMsg)
    except Exception as e:
        logging.error(f"Verify URL failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("")
async def receive_msg(
    msg_signature: str,
    timestamp: str,
    nonce: str,
    request: Request
):
    """
    企业微信消息/事件推送
    """
    # 读取请求体
    body = await request.body()
    
    try:
        # 使用封装后的方法统一处理消息接收
        message_info = wecom_service.handle_received_message(msg_signature, timestamp, nonce, body)
        logging.info(f"Structured message: {message_info}")
        
        # 使用 Agent 处理逻辑
        # 后续大模型将接收 message_info，并通过 send_text_message 回复
        await agent_manager.process_message(message_info)
        
        # 企业微信要求收到消息后必须回复 success 或者空字符串
        return Response(content="success", media_type="text/plain")
    except Exception as e:
        logging.error(f"Handle message failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

import os
import xml.etree.ElementTree as ET
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from app.wecom.crypto import WXBizMsgCrypt

# 加载环境变量
load_dotenv()

app = FastAPI()

# 企业微信配置
WECOM_TOKEN = os.getenv("WECOM_TOKEN", "")
WECOM_ENCODING_AES_KEY = os.getenv("WECOM_ENCODING_AES_KEY", "")
WECOM_CORP_ID = os.getenv("WECOM_CORP_ID", "")

# 初始化加密工具
wxcpt = WXBizMsgCrypt(WECOM_TOKEN, WECOM_ENCODING_AES_KEY, WECOM_CORP_ID)

@app.get("/callback")
async def verify_url(
    msg_signature: str,
    timestamp: str,
    nonce: str,
    echostr: str
):
    """
    企业微信验证URL有效性
    """
    ret, sReplyMsg = wxcpt.verify_url(msg_signature, timestamp, nonce, echostr)
    if ret != 0:
        raise HTTPException(status_code=400, detail=f"Verify URL failed: {ret}")
    
    # 验证成功，返回解密后的明文内容
    return PlainTextResponse(content=sReplyMsg)

@app.post("/callback")
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
    
    # 解析 XML 拿到 Encrypt 字段
    try:
        xml_data = ET.fromstring(body)
        encrypt_msg = xml_data.find("Encrypt").text
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid XML format")

    # 解密消息
    ret, sMsg = wxcpt.decrypt(encrypt_msg)
    if ret != 0:
        raise HTTPException(status_code=400, detail=f"Decrypt failed: {ret}")
    
    # 解析解密后的 XML
    # 这里可以根据业务逻辑处理不同的消息类型 (Text, Image, Event, etc.)
    print(f"Received message: {sMsg}")
    
    # 如果需要被动回复，可以构造 XML 并加密返回
    # 示例：简单回复 'success' 或空字符串表示已收到
    return Response(content="success", media_type="text/plain")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8099)

from app.wecom.crypto import WXBizMsgCrypt
from app.core.config import settings

# 初始化加密工具
wxcpt = WXBizMsgCrypt(
    settings.WECOM_TOKEN, 
    settings.WECOM_ENCODING_AES_KEY, 
    settings.WECOM_CORP_ID
)

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings:
    # 企业微信配置
    WECOM_TOKEN: str = os.getenv("WECOM_TOKEN", "")
    WECOM_ENCODING_AES_KEY: str = os.getenv("WECOM_ENCODING_AES_KEY", "")
    WECOM_CORP_ID: str = os.getenv("WECOM_CORP_ID", "")
    WECOM_CORP_SECRET: str = os.getenv("WECOM_CORP_SECRET", "")
    WECOM_AGENT_ID: str = os.getenv("WECOM_AGENT_ID", "")
    
    # 端口配置
    PORT: int = int(os.getenv("PORT", "8099"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

settings = Settings()

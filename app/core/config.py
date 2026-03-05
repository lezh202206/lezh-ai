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

    # LangSmith and LLM Configuration
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "true")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "qwen-plus")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "")

    
    # 端口配置
    PORT: int = int(os.getenv("PORT", "8099"))
    HOST: str = os.getenv("HOST", "0.0.0.0")

settings = Settings()

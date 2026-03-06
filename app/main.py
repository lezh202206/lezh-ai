import logging
from fastapi import FastAPI
from app.api.wecom import router as wecom_router
from app.core.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # 输出到标准流，Docker 会捕获它
    ],
    force=True  # 强制覆盖已有的日志配置 (如 uvicorn 的配置)
)

logger = logging.getLogger(__name__)

app = FastAPI(title="AI WeCom Integration Service")

# 注册 API 路由
app.include_router(wecom_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

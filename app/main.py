from fastapi import FastAPI
from app.api.wecom import router as wecom_router
from app.core.config import settings

app = FastAPI(title="AI WeCom Integration Service")

# 注册 API 路由
app.include_router(wecom_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

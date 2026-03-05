.PHONY: help install run test dev langsmith-start langsmith-stop

# 默认目标，显示帮助信息
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install          Install project dependencies from requirements.txt"
	@echo "  run              Run the FastAPI application with auto-reload"
	@echo "  test             Run pytest for all tests"
	@echo "  dev              Run LangGraph development server"
	@echo "  langsmith-start  Start LangSmith local instance with Docker"
	@echo "  langsmith-stop   Stop LangSmith local instance"

# 安装依赖
install:
	@echo "--> Installing dependencies..."
	pip install -r requirements.txt

# 运行应用
loc_run:
	@echo "--> Starting application on http://0.0.0.0:8099"
	uvicorn app.main:app --host 0.0.0.0 --port 8099 --reload

# 运行测试
test:
	@echo "--> Running tests..."
	pytest

# 运行 LangGraph 开发服务器
dev:
	@echo "--> Starting LangGraph development server..."
	langgraph dev --allow-blocking

## 启动 LangSmith 本地实例
langsmith-start:
	@echo "--> Starting LangSmith local instance..."
	docker compose up -d
#
## 停止 LangSmith 本地实例
langsmith-stop:
	@echo "--> Stopping LangSmith local instance..."
	docker compose down

# AI 企业微信集成服务 - 项目结构说明文档

本项目的重构旨在支持高可扩展性，并为未来接入 **LangChain** 和 **LangGraph** 建立清晰的职责分离。

## 目录结构预览

```text
/
├── app/                  # 应用主代码目录
│   ├── agents/           # AI 代理层：存放 LangChain/LangGraph 逻辑
│   │   ├── agent_manager.py      # Agent 管理器，调用具体的 Agent
│   │   ├── langgraph_agent.py  # LangGraph Agent 实现
│   │   └── tools.py            # LangChain 工具/Skills
│   ├── api/              # 路由层：定义 API 接口 (FastAPI)
│   │   └── wecom.py            # 企业微信回调接口实现
│   ├── core/             # 核心配置层：环境配置、工具初始化
│   │   ├── config.py            # 环境变量和全局配置管理
│   │   └── wecom_crypto.py      # 企业微信加密/解密对象初始化
│   ├── services/         # 业务逻辑层：消息处理、数据解析
│   │   ├── wecom_service.py     # 企业微信消息处理服务
│   │   ├── mcp_service.py       # 阿里云百炼 MCP 服务封装
│   │   └── jenkins_mcp_service.py # Jenkins 构建服务封装
│   ├── wecom/            # 企业微信 SDK 源码（加解密）
│   │   └── crypto.py            # 企业微信加解密实现
│   └── main.py           # 应用入口：挂载路由、启动服务
├── tests/                # 测试代码
│   ├── test_agent.py            # Agent 功能测试
│   ├── test_crypto.py           # 加密/解密功能测试
│   └── test_wecom_send.py       # 企业微信消息发送测试
├── .env                  # 环境变量配置 (本地开发，不提交)
├── .env.example          # 环境变量示例文件
├── .gitignore            # Git 忽略文件配置
├── DEPLOY.md             # 部署说明文档
├── Dockerfile            # Docker 构建文件
├── Makefile              # 项目管理命令
├── PROJECT_STRUCTURE.md  # 本文档
├── docker-compose.yml    # Docker Compose 配置文件
├── langgraph.json        # LangGraph 配置文件
├── pyproject.toml        # 项目配置文件 (包含 LangSmith 配置)
└── requirements.txt      # 依赖项
```

---

## 各层级详细职责描述

### 1. **Agent 层 (`app/agents/`)**
- **定位**: AI 智能体决策中心，负责所有的智能逻辑。
- **职责**: 
  - `langgraph_agent.py`: 使用 LangGraph 实现核心的状态图 (Graph)，负责编排 LLM 调用和工具调用。
  - `tools.py`: 定义可供 Agent 调用的工具 (Skills)，例如 `get_weather`。每个工具都应使用 `@tool` 装饰器。
  - `agent_manager.py`: 作为 Agent 的统一入口，接收来自 Service 层的消息，并将其分发给相应的 Agent (目前是 `langgraph_agent`) 进行处理。
- **扩展建议**: 
  - **新增 Skill**: 在 `tools.py` 中定义新函数并导出。
  - **新增 Agent**: 如果未来有多个 Agent，可以在 `agents` 目录下创建新的 `*_agent.py` 文件，并在 `agent_manager.py` 中实现路由逻辑。

### 2. **API 层 (`app/api/`)**
- **定位**: 外部通信接口。
- **职责**: 
  - 定义 HTTP 路由（如企业微信的回调接口）。
  - 处理 HTTP 请求的参数验证。
  - 调用 Service 层完成业务，并对外部返回响应。
- **关联文件**: `app/api/wecom.py`

### 3. **Service 层 (`app/services/`)**
- **定位**: 业务规则实现层。
- **职责**: 
  - 封装与外部服务（如企业微信 API、MCP 服务、Jenkins）的交互逻辑。
  - `wecom_service.py`: 负责企业微信消息的加解密、XML 解析、获取 Access Token、主动发送消息等。
  - `mcp_service.py`: 封装阿里云百炼 MCP 服务，提供天气查询等功能。
  - `jenkins_mcp_service.py`: 封装 Jenkins 构建服务，提供项目构建、部署等功能。
- **扩展建议**: 如果未来需要集成其他外部服务（如数据库、Redis、其他 MCP 服务），应在此处创建新的 `service` 文件。

### 4. **Core 层 (`app/core/`)**
- **定位**: 系统基础设施和全局配置。
- **职责**: 
  - `config.py`: 使用 Pydantic-Settings 管理环境变量和全局配置。增加了对 LangSmith 和 LLM 的配置。
  - `wecom_crypto.py`: 初始化全局唯一的企业微信加密/解密对象。

### 5. **WeCom SDK (`app/wecom/`)**
- **定位**: 企业微信官方提供的 Python SDK。
- **职责**: 提供基础的加密/解密/签名验证功能。

---

## 开发建议与流程

### 当需要增加新功能时（例如，一个新的 Skill）：
1. **新增环境变量** (如果需要): 在 `.env.example` 和 `.env` 中添加，并在 `app/core/config.py` 中定义。
2. **新增 AI 技能 (Skill)**: 在 `app/agents/tools.py` 中使用 `@tool` 装饰器定义一个新函数，并将其添加到 `tools` 列表中。
3. **测试 Skill**: 可以在 `langgraph_agent.py` 中直接测试，或通过企业微信发送特定指令来触发。
4. **调试与追踪**: 在 [LangSmith](https://smith.langchain.com/) 上观察 Agent 的执行流程，确保 Skill 被正确调用。

### 测试流程
1. **运行测试**: 使用 `pytest` 命令运行测试，确保所有功能正常。
2. **测试文件说明**:
   - `test_agent.py`: 测试 Agent 功能，确保智能体能够正确处理消息。
   - `test_crypto.py`: 测试企业微信加解密功能，确保消息安全。
   - `test_wecom_send.py`: 测试企业微信消息发送功能，确保消息能够正确发送。

### Docker 部署
1. **构建镜像**: 使用 `docker build -t wecom-ai-agent .` 构建 Docker 镜像。
2. **运行容器**: 使用 `docker-compose up -d` 启动服务。
3. **配置**: 通过 `.env` 文件配置环境变量，或在 `docker-compose.yml` 中设置。
4. **服务信息**:
   - 容器名称: `wecom-callback`
   - 端口映射: `8099:8099`
   - 重启策略: `always`
   - 环境变量: 从 `.env` 文件加载
5. **基础镜像**: `python:3.11-slim`
6. **运行命令**: `uvicorn app.main:app --host 0.0.0.0 --port 8099`

---

## 依赖说明
- **FastAPI**: 用于提供高性能的 API 服务。
- **Uvicorn**: ASGI 服务器，用于运行 FastAPI 应用。
- **Cryptography**: 企业微信加解密必需。
- **Python-dotenv**: 用于加载环境变量。
- **LangChain**: 用于构建和管理 AI 智能体。
- **LangGraph**: 用于构建和编排智能体的状态图逻辑。
- **LangGraph-CLI**: LangGraph 命令行工具。
- **LangChain-OpenAI**: LangChain 与 OpenAI 模型的集成。
- **LangChain-Community**: LangChain 社区工具和集成。
- **DashScope**: 阿里云通义千问模型官方 SDK。
- **LangSmith**: 用于 Agent 的调试、追踪和监控。
- **Pydantic-Settings**: 用于管理环境变量和配置。
- **HTTPX**: 用于异步 HTTP 请求（在 `wecom_service.py` 中使用）。
- **Respx**: 用于模拟 HTTP 请求，用于测试。
- **Pytest-asyncio**: 用于测试异步代码。

# AI 企业微信集成服务 - 项目结构说明文档

本项目的重构旨在支持高可扩展性，并为未来接入 **LangChain** 和 **LangGraph** 建立清晰的职责分离。

## 目录结构预览

```text
/
├── app/                  # 应用主代码目录
│   ├── agents/           # AI 代理层：存放 LangChain/LangGraph 逻辑
│   ├── api/              # 路由层：定义 API 接口 (FastAPI)
│   ├── core/             # 核心配置层：环境配置、工具初始化
│   ├── services/         # 业务逻辑层：消息处理、数据解析
│   ├── wecom/            # 企业微信 SDK 源码（加解密）
│   └── main.py           # 应用入口：挂载路由、启动服务
├── tests/                # 测试代码
├── .env                  # 环境变量配置
├── requirements.txt      # 依赖项
└── PROJECT_STRUCTURE.md  # 本文档
```

---

## 各层级详细职责描述

### 1. **Agent 层 (`app/agents/`)**
- **定位**: AI 智能体决策中心。
- **职责**: 
  - 定义 LangChain 的 Chains。
  - 实现 LangGraph 的状态图 (Graphs)。
  - 处理上下文记忆 (Memory)。
- **扩展建议**: 如果未来有多个场景（如：客服、报表生成），可以按场景分子目录，例如 `app/agents/customer_service/`。

### 2. **API 层 (`app/api/`)**
- **定位**: 外部通信接口。
- **职责**: 
  - 定义 HTTP 路由。
  - 处理参数验证。
  - 调用 Service 层完成业务。
- **关联文件**: [wecom.py](file:///Users/lezh/Desktop/AI/ai/app/api/wecom.py)

### 3. **Service 层 (`app/services/`)**
- **定位**: 业务规则实现层。
- **职责**: 
  - 企业微信消息的加解密与 XML 解析。
  - 获取 Access Token 并缓存。
  - 主动发送消息（如文本消息）。
  - 复杂业务逻辑的封装（如：多媒体文件上传下载）。
- **关联文件**: [wecom_service.py](file:///Users/lezh/Desktop/AI/ai/app/services/wecom_service.py)

### 4. **Core 层 (`app/core/`)**
- **定位**: 系统基础设施。
- **职责**: 
  - [config.py](file:///Users/lezh/Desktop/AI/ai/app/core/config.py): 管理环境变量和全局配置。
  - [wecom_crypto.py](file:///Users/lezh/Desktop/AI/ai/app/core/wecom_crypto.py): 初始化全局唯一的企业微信加密对象。

### 5. **WeCom SDK (`app/wecom/`)**
- **定位**: 企业微信官方提供的 Python SDK。
- **职责**: 提供基础的加密/解密/签名验证功能。

---

## 开发建议与流程

### 当需要增加新功能时：
1. **新增环境变量**: 修改 `.env` 并在 `app/core/config.py` 中定义。
2. **新增 AI 技能**: 在 `app/agents/` 下实现逻辑，并在 `AgentManager` 中注册。
3. **处理新的消息类型**: 在 `app/services/wecom_service.py` 中扩展解析逻辑。
4. **新增 API 接口**: 在 `app/api/` 下创建新路由，并在 `app/main.py` 中挂载。

---

## 依赖说明
- **FastAPI**: 用于提供高性能的 API 服务。
- **LangChain/LangGraph**: 用于构建智能体逻辑（已在 `requirements.txt` 中预设）。
- **Cryptography**: 企业微信加解密必需。

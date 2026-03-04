# 腾讯云部署说明文档

## 1. 准备工作

### 1.1 获取企业微信回调参数
在 [企业微信后台](https://work.weixin.qq.com/wework_admin/login) 的自建应用中，开启“接收消息”功能，获取以下三个关键参数：
- **Token**: 自定义字符串
- **EncodingAESKey**: 随机生成的 43 位字符
- **CorpID**: 企业 ID

### 1.2 准备腾讯云环境
- 建议使用 **腾讯云轻量应用服务器 (Lighthouse)** 或 **云服务器 (CVM)**。
- 操作系统推荐使用 **Ubuntu 20.04+** 或 **CentOS 7.6+**。
- 确保已安装 **Docker** 和 **Docker Compose**。

---

## 2. 部署步骤

### 2.1 克隆代码
将本项目上传或克隆到服务器：
```bash
git clone <your_repo_url>
cd wecom-callback
```

### 2.2 配置环境变量
创建 `.env` 文件并填入参数：
```bash
cp .env.example .env
vim .env
```
修改 `.env` 中的内容：
```env
WECOM_TOKEN=你的Token
WECOM_ENCODING_AES_KEY=你的EncodingAESKey
WECOM_CORP_ID=你的企业CorpID
```

### 2.3 启动服务
使用 Docker Compose 一键启动：
```bash
docker-compose up -d --build
```

---

## 3. 网络与安全组设置

### 3.1 开放端口
- 在腾讯云后台安全组中，开放 **8099** 端口。
- 如果需要使用 80/443 端口，建议使用 Nginx 反向代理。

### 3.2 配置域名（可选但推荐）
由于企业微信回调必须使用公网可访问的 URL，建议配置域名并使用 HTTPS。

#### Nginx 反代示例：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8099;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 4. 在企业微信后台配置回调 URL

- **URL**: `http://你的公网IP或域名/callback`
- **Token**: 与 `.env` 中一致
- **EncodingAESKey**: 与 `.env` 中一致

点击保存，如果服务器配置正确且服务已启动，企业微信会提示“验证成功”。

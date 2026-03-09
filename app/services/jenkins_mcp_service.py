import json
import datetime
from typing import Any, Dict, List, Optional
from dashscope import Generation
from dashscope.api_entities.dashscope_response import GenerationResponse
from app.core.config import settings

# 懒加载 jenkins 模块，避免在未安装时导入失败
jenkins = None
try:
    import jenkins
except ImportError:
    pass


class JenkinsMCPService:
    """
    Jenkins MCP 服务封装
    使用 python-jenkins 库实现 Jenkins 构建任务
    """

    def __init__(self):
        # 加载配置
        self.api_key = settings.BAILIAN_MCP_API_KEY or settings.DASHSCOPE_API_KEY
        self.model = settings.LLM_MODEL_NAME
        self.jenkins_url = getattr(settings, 'JENKINS_URL', '')
        self.jenkins_username = getattr(settings, 'JENKINS_USERNAME', '')
        self.jenkins_password = getattr(settings, 'JENKINS_PASSWORD', '')
        self.jenkins_token = getattr(settings, 'JENKINS_TOKEN', '')
        
        # 配置项目名称处理规则
        self.common_suffixes = ["-service", "-mq", "-scheduler"]

    def is_configured(self) -> bool:
        """
        检查 MCP 服务是否已配置
        """
        return bool(self.api_key)

    def is_jenkins_configured(self) -> bool:
        """
        检查 Jenkins 是否已配置
        """
        return bool(self.jenkins_url) and bool(self.jenkins_username) and bool(self.jenkins_password)

    def _get_tools(self) -> List[Dict[str, Any]]:
        """
        获取工具定义列表
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "build_jenkins",
                    "description": "执行 Jenkins 构建任务，可以指定项目、环境、分支和服务名。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project": {
                                "type": "string",
                                "description": "项目名称，比如 项目A、项目B 等。",
                            },
                            "environment": {
                                "type": "string",
                                "description": "环境名称，比如 测试环境、生产环境、dev、test、prod 等。",
                            },
                            "branch": {
                                "type": "string",
                                "description": "分支名称，比如 master、test、develop 等。",
                            },
                            "service_name": {
                                "type": "string",
                                "description": "服务名称，比如 order、user、payment 等。",
                            }
                        },
                        "required": ["project", "environment", "branch", "service_name"],
                    },
                },
            }
        ]

    def _get_job_name(self, project: str, service_name: str) -> str:
        """
        根据项目名称和服务名生成 Jenkins 任务名称
        """
        if "-" in project and not any(project.endswith(suffix) for suffix in self.common_suffixes):
            return project
        
        if service_name:
            return f"{project}-{service_name}"
        return project

    def _get_build_params(self, branch: str, environment: str, service_name: str) -> Dict[str, str]:
        """
        生成 Jenkins 构建参数
        """
        params = {
            "BRANCH": branch
        }
        
        if environment:
            params["ENV"] = environment
        if service_name:
            params["SERVICENAME"] = service_name
            
        return params

    def _build_jenkins(self, project: str, environment: str, branch: str, service_name: str) -> str:
        """
        执行 Jenkins 构建的实际实现
        调用 Jenkins API 执行构建任务
        """
        # 检查配置
        if not self.is_jenkins_configured():
            return json.dumps({
                "success": False,
                "message": "Jenkins 服务未配置，请联系管理员。"
            }, ensure_ascii=False)
        
        # 检查 jenkins 模块
        if jenkins is None:
            return json.dumps({
                "success": False,
                "message": "Jenkins 模块未安装，请联系管理员。"
            }, ensure_ascii=False)
        
        try:
            # 连接 Jenkins 服务器
            server = jenkins.Jenkins(
                self.jenkins_url,
                username=self.jenkins_username,
                password=self.jenkins_password
            )
            
            # 生成任务名称和构建参数
            job_name = self._get_job_name(project, service_name)
            params = self._get_build_params(branch, environment, service_name)
            
            # 触发构建
            build_number = server.build_job(job_name, parameters=params)
            
            # 构建结果
            build_data = {
                "success": True,
                "message": f"成功触发 Jenkins 构建任务：{job_name}",
                "project": project,
                "environment": environment,
                "branch": branch,
                "service_name": service_name,
                "job_name": job_name,
                "build_number": build_number,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(build_data, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "message": f"Jenkins 构建失败：{str(e)}",
                "project": project,
                "environment": environment,
                "branch": branch,
                "service_name": service_name
            }, ensure_ascii=False)

    def _call_model(self, messages: List[Dict[str, Any]]) -> GenerationResponse:
        """
        调用通义千问模型
        """
        return Generation.call(
            api_key=self.api_key,
            model=self.model,
            messages=messages,
            result_format="message",
        )

    def build_jenkins(self, project: str, environment: str, branch: str, service_name: str) -> str:
        """
        使用 MCP 服务执行 Jenkins 构建任务
        通过 DashScope SDK Function Calling 实现
        支持指定项目、环境、分支和服务名
        """
        # 检查配置
        if not self.is_configured():
            return "MCP 服务未配置，请联系管理员。"

        # 构建消息
        messages = [{
            "role": "user",
            "content": f"执行 Jenkins 构建：项目{project}，环境{environment}，分支{branch}，服务名{service_name}"
        }]

        try:
            # 执行构建
            tool_result = self._build_jenkins(project, environment, branch, service_name)

            # 构建消息
            build_data_message = {
                "role": "user",
                "content": f"Jenkins 构建结果：{tool_result}\n\n请根据以上构建结果，生成一个自然、友好的构建报告。包含构建状态、任务名称、构建编号等信息，并提供相应的后续操作建议。"
            }

            messages.append(build_data_message)

            # 调用模型生成报告
            response = self._call_model(messages)

            # 处理响应
            if response.status_code != 200:
                return f"Jenkins 构建服务暂时不可用，请稍后再试。（错误码: {response.status_code}）"

            final_output = response.output.choices[0].message
            return final_output.get("content", "无法生成构建报告，请稍后再试。")

        except Exception as e:
            return f"Jenkins 构建出错：{str(e)}"


jenkins_mcp_service = JenkinsMCPService()

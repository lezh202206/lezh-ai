from langchain_core.tools import tool

from app.services.jenkins_mcp_service import jenkins_mcp_service
from app.services.mcp_service import mcp_service


@tool
def get_weather(city: str, time_range: str = "today") -> str:
    """
    获取指定城市的天气信息。
    支持查询不同时间范围的天气。
    
    Args:
        city: 城市名称，例如：北京、上海
        time_range: 查询时间范围，可选值：today（今天）、yesterday（昨天）、last_3_days（近3天）、last_7_days（近7天）、tomorrow（明天）、next_3_days（未来3天）、next_7_days（未来7天）
    
    Returns:
        天气信息
    """
    return mcp_service.get_weather(city, time_range)


@tool
def jenkins_build(project: str, environment: str, branch: str, service_name: str) -> str:
    """
    触发 Jenkins 项目构建。
    支持指定项目、环境、分支和服务名。

    Args:
        project: 项目名称，例如：project-A
        environment: 环境名称，例如：dev、test、prod
        branch: 代码分支，例如：master、test、feature-xxx
        service_name: 服务名称，例如：order、customer、merchant

    Returns:
        构建结果信息
    """
    return jenkins_mcp_service.build_jenkins(project, environment, branch, service_name)


tools = [get_weather, jenkins_build]

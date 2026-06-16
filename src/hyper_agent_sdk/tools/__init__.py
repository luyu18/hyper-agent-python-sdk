"""
工具调用组件
============
提供标准化的工具定义与调用接口。
插件可通过注册工具扩展智能体能力。
"""
from hyper_agent_sdk.tools.base import Tool, ToolResult
from hyper_agent_sdk.tools.builtins import BUILTIN_TOOLS

__all__ = ["Tool", "ToolResult", "BUILTIN_TOOLS"]

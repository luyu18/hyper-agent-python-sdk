"""
Hyper-Agent SDK — 开源插件开发工具包
====================================
供外部开发者基于标准接口开发扩展插件。
仅提供公开API接口，不可访问内核内部调度逻辑。

GitHub: https://github.com/luyu18/hyper-agent-python-sdk
License: MIT
"""
from hyper_agent_sdk.plugin_base import HyperAgentPlugin, PluginInfo, register_plugin
from hyper_agent_sdk.types import (
    TaskRequest,
    TaskResponse,
    TaskStatus,
    ModelConfig,
    ToolDefinition,
    WorkflowStep,
    MemoryEntry,
    PluginManifest,
    # v0.2 — 权限令牌体系
    TokenScope,
    CapabilityToken,
    PublicCapabilities,
)

__version__ = "0.2.0"
__all__ = [
    # 插件
    "HyperAgentPlugin",
    "PluginInfo",
    "register_plugin",
    # 类型
    "TaskRequest",
    "TaskResponse",
    "TaskStatus",
    "ModelConfig",
    "ToolDefinition",
    "WorkflowStep",
    "MemoryEntry",
    "PluginManifest",
    # 权限 (v0.2)
    "TokenScope",
    "CapabilityToken",
    "PublicCapabilities",
]

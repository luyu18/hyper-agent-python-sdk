"""
Hyper-Agent SDK — 开源插件开发工具包
====================================
供外部开发者基于标准接口开发扩展插件。
仅提供公开API接口，不可访问内核内部调度逻辑。

GitHub: https://github.com/hyper-agent/sdk
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
)

__version__ = "0.1.0"
__all__ = [
    "HyperAgentPlugin",
    "PluginInfo",
    "register_plugin",
    "TaskRequest",
    "TaskResponse",
    "TaskStatus",
    "ModelConfig",
    "ToolDefinition",
    "WorkflowStep",
    "MemoryEntry",
    "PluginManifest",
]

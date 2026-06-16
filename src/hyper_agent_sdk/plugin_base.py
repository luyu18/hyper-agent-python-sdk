"""
Hyper-Agent SDK 插件基类
========================
外部开发者继承此基类开发插件。
提供标准化的生命周期管理和API调用接口。
"""
from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from hyper_agent_sdk.types import (
    TaskRequest,
    TaskResponse,
    ToolDefinition,
    PluginManifest,
    MemoryEntry,
)

logger = logging.getLogger("hyper_agent.plugin")


@dataclass
class PluginInfo:
    """插件信息"""
    plugin_id: str
    name: str
    version: str
    description: str


class HyperAgentPlugin(ABC):
    """
    Hyper-Agent 插件基类
    
    所有插件必须继承此类并实现抽象方法。
    插件仅能通过以下公开API与内核通信：
    
    公开API:
    - submit_task()         提交任务
    - search_memory()       搜索记忆
    - add_memory()         写入记忆
    - invoke_model()       调用模型
    - get_config()         获取配置
    - emit_event()         发布事件
    
    禁止访问的API:
    - 修改调度器规则
    - 修改内核配置
    - 直接操作事件总线内部
    - 修改压缩器行为
    """
    
    def __init__(self, manifest: PluginManifest):
        self._manifest = manifest
        self._kernel_api: Optional[Callable] = None  # 由内核注入
        self._initialized = False
    
    @property
    def manifest(self) -> PluginManifest:
        return self._manifest
    
    @property
    def plugin_id(self) -> str:
        return self._manifest.plugin_id
    
    @property
    def plugin_name(self) -> str:
        return self._manifest.name
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized
    
    # ==================== 抽象方法（子类必须实现） ====================
    
    @abstractmethod
    async def on_initialize(self) -> None:
        """插件初始化回调"""
        ...
    
    @abstractmethod
    async def on_shutdown(self) -> None:
        """插件关闭回调"""
        ...
    
    @abstractmethod
    async def on_task_request(self, task: TaskRequest) -> TaskResponse:
        """
        处理任务请求（插件核心逻辑）
        
        Args:
            task: 任务请求
        
        Returns:
            TaskResponse
        """
        ...
    
    # ==================== 可选覆写方法 ====================
    
    async def on_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """事件通知回调（可选覆写）"""
        pass
    
    async def on_config_change(self, key: str, value: Any) -> None:
        """配置变更回调（可选覆写）"""
        pass
    
    # ==================== 公开API（供插件调用内核） ====================
    
    async def submit_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: str = "normal",
    ) -> TaskResponse:
        """
        提交任务到内核调度器
        
        这是插件与内核的主要交互方式。
        内核负责选择模型、调度执行、返回结果。
        """
        if not self._kernel_api:
            raise RuntimeError("Plugin not connected to kernel. Call connect() first.")
        
        return await self._kernel_api("task.submit", {
            "plugin_id": self.plugin_id,
            "task_type": task_type,
            "payload": payload,
            "priority": priority,
        })
    
    async def search_memory(
        self,
        query: str,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """搜索记忆系统（摘要归档层）"""
        self._check_connected()
        return await self._kernel_api("memory.search", {
            "plugin_id": self.plugin_id,
            "query": query,
            "top_k": top_k,
        })
    
    async def add_memory(self, role: str, content: str) -> None:
        """写入记忆"""
        self._check_connected()
        await self._kernel_api("memory.add_message", {
            "plugin_id": self.plugin_id,
            "role": role,
            "content": content,
        })
    
    async def invoke_model(
        self,
        model_name: str,
        prompt: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """调用指定模型"""
        self._check_connected()
        return await self._kernel_api("model.invoke", {
            "plugin_id": self.plugin_id,
            "model": model_name,
            "prompt": prompt,
            "params": kwargs,
        })
    
    async def get_config(self, key: Optional[str] = None) -> Any:
        """获取配置（仅公开配置项）"""
        self._check_connected()
        return await self._kernel_api("config.get", {
            "plugin_id": self.plugin_id,
            "key": key,
        })
    
    async def emit_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """发布事件（仅公开事件类型）"""
        self._check_connected()
        await self._kernel_api("event.subscribe", {
            "plugin_id": self.plugin_id,
            "event_type": event_type,
            "payload": payload,
        })
    
    async def get_tools(self) -> List[ToolDefinition]:
        """获取当前插件提供的工具列表"""
        return []
    
    # ==================== 生命周期管理 ====================
    
    async def connect(self, kernel_api: Callable) -> None:
        """
        连接到内核（由框架自动调用，插件无需手动调用）
        
        Args:
            kernel_api: 内核API调用函数
        """
        self._kernel_api = kernel_api
        self._initialized = True
        await self.on_initialize()
        logger.info("Plugin connected: %s", self.plugin_id)
    
    async def disconnect(self) -> None:
        """断开连接"""
        await self.on_shutdown()
        self._kernel_api = None
        self._initialized = False
        logger.info("Plugin disconnected: %s", self.plugin_id)
    
    def _check_connected(self):
        """检查是否已连接内核"""
        if not self._kernel_api or not self._initialized:
            raise RuntimeError(
                f"Plugin '{self.plugin_id}' is not connected to Hyper-Agent kernel. "
                "Ensure the plugin is registered via PluginRegistry."
            )
    
    # ==================== 工具方法 ====================
    
    @classmethod
    def get_manifest_template(cls) -> Dict[str, Any]:
        """获取插件清单模板"""
        return {
            "plugin_id": "my-plugin",
            "name": "My Plugin",
            "version": "0.1.0",
            "description": "A Hyper-Agent plugin",
            "author": "",
            "license": "MIT",
            "capabilities": [],
            "dependencies": [],
            "min_sdk_version": "0.1.0",
        }
    
    def get_info(self) -> PluginInfo:
        """获取插件基本信息"""
        return PluginInfo(
            plugin_id=self.plugin_id,
            name=self.plugin_name,
            version=self._manifest.version,
            description=self._manifest.description,
        )


def register_plugin(plugin_class: type, kernel_api: Callable = None):
    """
    插件注册装饰器
    
    Usage:
        @register_plugin
        class MyPlugin(HyperAgentPlugin):
            ...
    """
    return plugin_class

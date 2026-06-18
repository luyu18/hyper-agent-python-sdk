"""
Hyper-Agent SDK 类型定义
========================
插件开发所需的所有数据模型和类型定义。
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskRequest:
    """任务请求"""
    task_id: str
    task_type: str         # reasoning / generation / compression / analysis / tool_call
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: str = "normal"  # low / normal / high / critical
    context: Optional[List[Dict[str, str]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "payload": self.payload,
            "priority": self.priority,
            "metadata": self.metadata,
        }


@dataclass
class TaskResponse:
    """任务响应"""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: int = 0
    elapsed_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "success": self.success,
            "result": str(self.result)[:500] if self.result else None,
            "error": self.error,
            "model_used": self.model_used,
            "tokens_used": self.tokens_used,
            "elapsed_ms": self.elapsed_ms,
        }


@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    provider: str              # deepseek / glm / openai / anthropic / ...
    api_key_env: str           # 环境变量名（安全实践）
    api_base: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolDefinition:
    """工具定义"""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema格式
    handler: Optional[str] = None  # 处理函数名
    
    def to_openai_format(self) -> Dict[str, Any]:
        """转换为OpenAI Function Calling格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass
class WorkflowStep:
    """工作流步骤"""
    step_id: str
    name: str
    description: str = ""
    task_type: str = "reasoning"
    depends_on: List[str] = field(default_factory=list)  # 依赖步骤ID列表
    condition: Optional[str] = None   # 条件表达式
    retry_on_failure: bool = True
    timeout_seconds: int = 300


@dataclass
class MemoryEntry:
    """记忆条目（用于插件访问记忆系统）"""
    role: str
    content: str
    timestamp: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PluginManifest:
    """插件清单"""
    plugin_id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    license: str = "MIT"
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    min_sdk_version: str = "0.1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "license": self.license,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "min_sdk_version": self.min_sdk_version,
        }


# ══════════════════════════════════════════════════════════════════════
# 权限令牌体系 (Capability Token) — v0.2 新增
# ══════════════════════════════════════════════════════════════════════

class TokenScope(Enum):
    """Token 作用域"""
    KERNEL = "kernel"           # 内核级（仅框架自身）
    PLUGIN = "plugin"           # 插件级（沙箱隔离）
    DELEGATED = "delegated"     # 委派级（临时权限）


@dataclass
class CapabilityToken:
    """
    能力令牌 — 内核调用 open_session 下发给插件的授权凭证

    插件不需要自己创建令牌，内核会在插件初始化时自动下发。
    插件只需要在调用 API 时将令牌传入即可。
    """
    token_id: str = ""
    owner_id: str = ""               # 持有者标识（插件ID）
    scope: TokenScope = TokenScope.PLUGIN
    allowed_apis: Set[str] = field(default_factory=set)
    denied_apis: Set[str] = field(default_factory=set)
    max_memory_mb: int = 512
    max_cpu_percent: int = 50
    allow_network: bool = True
    allow_file_write: bool = False
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    delegated_by: Optional[str] = None   # 委派来源
    audit_enabled: bool = True

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def can_access(self, api_name: str) -> bool:
        """检查是否可以访问指定 API"""
        if api_name in self.denied_apis:
            return False
        if api_name in self.allowed_apis:
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token_id": self.token_id,
            "owner_id": self.owner_id,
            "scope": self.scope.value,
            "allowed_apis": list(self.allowed_apis),
            "denied_apis": list(self.denied_apis),
            "expires_at": self.expires_at,
            "delegated_by": self.delegated_by,
        }


class PublicCapabilities:
    """插件可申请调用的公开 API 列表（v0.2 与内核对齐）"""
    PLUGIN_REGISTER = "plugin.register"
    TASK_SUBMIT = "task.submit"
    MEMORY_ADD = "memory.add_message"
    MEMORY_SEARCH = "memory.search"
    MODEL_INVOKE = "model.invoke"
    EVENT_SUBSCRIBE = "event.subscribe"
    TOOL_EXECUTE = "tool.execute"

    ALL: Set[str] = {
        PLUGIN_REGISTER, TASK_SUBMIT, MEMORY_ADD,
        MEMORY_SEARCH, MODEL_INVOKE, EVENT_SUBSCRIBE, TOOL_EXECUTE,
    }

    @classmethod
    def descriptions(cls) -> Dict[str, str]:
        """返回每个 API 的中文说明"""
        return {
            cls.PLUGIN_REGISTER: "注册插件到智能体集群",
            cls.TASK_SUBMIT: "提交任务到智能体集群",
            cls.MEMORY_ADD: "写入记忆到三层记忆系统",
            cls.MEMORY_SEARCH: "搜索历史摘要记忆",
            cls.MODEL_INVOKE: "调用指定大模型",
            cls.EVENT_SUBSCRIBE: "订阅系统事件",
            cls.TOOL_EXECUTE: "执行工具调用",
        }

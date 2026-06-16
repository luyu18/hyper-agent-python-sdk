"""
Hyper-Agent SDK 类型定义
========================
插件开发所需的所有数据模型和类型定义。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


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

"""
工具基类
========
定义所有工具的标准接口。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from hyper_agent_sdk.types import ToolDefinition


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": str(self.output)[:500] if self.output else None,
            "error": self.error,
        }


class Tool(ABC):
    """
    工具基类
    
    插件可通过继承此类定义自定义工具。
    
    使用示例:
        class WebSearchTool(Tool):
            def get_definition(self):
                return ToolDefinition(
                    name="web_search",
                    description="搜索互联网信息",
                    parameters={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "搜索关键词"},
                        },
                        "required": ["query"],
                    },
                )
            
            async def execute(self, **params):
                query = params.get("query")
                result = await search_web(query)
                return ToolResult(success=True, output=result)
    """
    
    @abstractmethod
    def get_definition(self) -> ToolDefinition:
        """获取工具定义"""
        ...
    
    @abstractmethod
    async def execute(self, **params) -> ToolResult:
        """执行工具"""
        ...
    
    @property
    def name(self) -> str:
        return self.get_definition().name
    
    @property
    def description(self) -> str:
        return self.get_definition().description

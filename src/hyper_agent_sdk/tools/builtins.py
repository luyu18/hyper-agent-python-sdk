"""
内置工具集
==========
Hyper-Agent 内置的常用工具。
插件开发时可作为参考实现。
"""
from __future__ import annotations

import json
import math
import time
from datetime import datetime
from typing import Any, Dict, List

from hyper_agent_sdk.tools.base import Tool, ToolResult
from hyper_agent_sdk.types import ToolDefinition


class CalculatorTool(Tool):
    """数学计算工具"""
    
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="calculator",
            description="执行数学计算。支持基本运算、三角函数、对数等。",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如 '2+3*4' 或 'sqrt(16)'",
                    },
                },
                "required": ["expression"],
            },
        )
    
    async def execute(self, **params) -> ToolResult:
        expression = params.get("expression", "")
        try:
            # 安全计算（仅允许数学函数）
            allowed_names = {
                k: v for k, v in math.__dict__.items()
                if not k.startswith("_")
            }
            allowed_names["abs"] = abs
            allowed_names["round"] = round
            allowed_names["int"] = int
            allowed_names["float"] = float
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return ToolResult(success=True, output=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class DateTimeTool(Tool):
    """日期时间工具"""
    
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="datetime",
            description="获取当前日期时间或进行日期计算。",
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["now", "today", "weekday", "format"],
                        "description": "操作类型",
                    },
                    "format_str": {
                        "type": "string",
                        "description": "日期格式（当action=format时使用）",
                    },
                },
                "required": ["action"],
            },
        )
    
    async def execute(self, **params) -> ToolResult:
        action = params.get("action", "now")
        now = datetime.now()
        
        if action == "now":
            return ToolResult(success=True, output=now.isoformat())
        elif action == "today":
            return ToolResult(success=True, output=now.strftime("%Y-%m-%d"))
        elif action == "weekday":
            days_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            return ToolResult(success=True, output=days_cn[now.weekday()])
        elif action == "format":
            fmt = params.get("format_str", "%Y-%m-%d %H:%M:%S")
            return ToolResult(success=True, output=now.strftime(fmt))
        else:
            return ToolResult(success=False, error=f"Unknown action: {action}")


class JSONTool(Tool):
    """JSON处理工具"""
    
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="json_tool",
            description="解析或格式化JSON数据。",
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["parse", "format", "validate"],
                        "description": "操作类型",
                    },
                    "data": {
                        "type": "string",
                        "description": "JSON字符串",
                    },
                },
                "required": ["action", "data"],
            },
        )
    
    async def execute(self, **params) -> ToolResult:
        action = params.get("action")
        data_str = params.get("data", "")
        
        try:
            if action == "parse":
                obj = json.loads(data_str)
                return ToolResult(success=True, output=obj)
            elif action == "format":
                obj = json.loads(data_str)
                formatted = json.dumps(obj, ensure_ascii=False, indent=2)
                return ToolResult(success=True, output=formatted)
            elif action == "validate":
                json.loads(data_str)
                return ToolResult(success=True, output="Valid JSON")
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")
        except json.JSONDecodeError as e:
            return ToolResult(success=False, error=str(e))


# 内置工具注册表
BUILTIN_TOOLS: List[Tool] = [
    CalculatorTool(),
    DateTimeTool(),
    JSONTool(),
]

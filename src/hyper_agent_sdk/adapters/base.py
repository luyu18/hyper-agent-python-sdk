"""
模型适配器基类
=============
定义所有模型适配器的标准接口。
任何大语言模型接入Hyper-Agent都需要实现此接口。
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Dict, List, Optional

from hyper_agent_sdk.types import ModelConfig, ToolDefinition


@dataclass
class ModelResponse:
    """模型响应"""
    content: str
    model: str
    tokens_prompt: int = 0
    tokens_completion: int = 0
    total_tokens: int = 0
    finish_reason: str = "stop"  # stop / length / tool_calls / error
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    elapsed_ms: float = 0.0
    raw_response: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "tokens_prompt": self.tokens_prompt,
            "tokens_completion": self.tokens_completion,
            "total_tokens": self.total_tokens,
            "finish_reason": self.finish_reason,
            "tool_calls": self.tool_calls,
            "elapsed_ms": self.elapsed_ms,
        }


class ModelAdapter(ABC):
    """
    模型适配器基类
    
    子类只需实现 chat() 方法。
    支持同步和异步调用模式。
    
    使用示例:
        class MyModelAdapter(ModelAdapter):
            async def chat(self, messages, **kwargs):
                # 调用你的模型API
                response = await my_api_call(messages)
                return ModelResponse(content=response)
    """
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self._total_tokens = 0
        self._total_calls = 0
        self._total_errors = 0
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[ToolDefinition]] = None,
        **kwargs,
    ) -> ModelResponse:
        """
        发送消息并获取回复
        
        Args:
            messages: [{"role": "user", "content": "..."}, ...]
            tools: 可选工具列表
            **kwargs: 额外参数
        
        Returns:
            ModelResponse
        """
        ...
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        流式对话（可选覆写）
        
        默认实现通过非流式chat拼接，子类可覆写实现真正流式。
        """
        response = await self.chat(messages, **kwargs)
        # 模拟流式输出
        words = response.content
        chunk_size = 10
        for i in range(0, len(words), chunk_size):
            yield words[i:i + chunk_size]
    
    async def compress(
        self,
        context: str,
        preserve_keywords: List[str],
    ) -> ModelResponse:
        """
        上下文压缩（可选覆写）
        
        默认由内核Compressor处理，子类可覆写实现专用压缩逻辑。
        """
        prompt = f"""请从以下上下文中提取结构化摘要，仅保留关键信息。

保留关键词：{', '.join(preserve_keywords)}

上下文：
{context}

输出JSON格式的结构化摘要，仅JSON不要其他："""
        
        return await self.chat([{"role": "user", "content": prompt}])
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        return {
            "model": self.config.name,
            "total_tokens": self._total_tokens,
            "total_calls": self._total_calls,
            "total_errors": self._total_errors,
            "error_rate": round(self._total_errors / max(self._total_calls, 1), 4),
        }
    
    async def health_check(self) -> bool:
        """健康检查（可选覆写）"""
        try:
            response = await self.chat(
                [{"role": "user", "content": "ping"}],
                max_tokens=5,
            )
            return response.finish_reason != "error"
        except Exception:
            return False

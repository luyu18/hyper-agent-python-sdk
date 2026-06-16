"""
DeepSeek API 模型适配器
========================
接入DeepSeek API（deepseek-v3等）。
使用 OpenAI 兼容接口。
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import aiohttp

from hyper_agent_sdk.adapters.base import ModelAdapter, ModelResponse
from hyper_agent_sdk.types import ModelConfig, ToolDefinition

logger = logging.getLogger("hyper_agent.adapter.deepseek")

DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"


class DeepSeekAdapter(ModelAdapter):
    """
    DeepSeek API适配器
    
    支持的模型:
    - deepseek-chat (deepseek-v3)
    - deepseek-reasoner (deepseek-r1)
    
    环境变量:
    - DEEPSEEK_API_KEY: API密钥
    
    配置示例:
        config = ModelConfig(
            name="deepseek-chat",
            provider="deepseek",
            api_key_env="DEEPSEEK_API_KEY",
            max_tokens=4096,
            temperature=0.7,
        )
        adapter = DeepSeekAdapter(config)
    """
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self._api_key = os.environ.get(config.api_key_env, "")
        self._api_base = config.api_base or DEEPSEEK_API_BASE
        
        if not self._api_key:
            logger.warning(
                "DEEPSEEK_API_KEY not set. Set env var %s or pass api_key.",
                config.api_key_env
            )
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[ToolDefinition]] = None,
        **kwargs,
    ) -> ModelResponse:
        start = time.time()
        
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.config.name,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "stream": False,
        }
        
        if tools:
            payload["tools"] = [t.to_openai_format() for t in tools]
        
        extra = self.config.extra_params
        if extra:
            payload.update(extra)
        
        self._total_calls += 1
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._api_base}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        self._total_errors += 1
                        logger.error("DeepSeek API error %d: %s", resp.status, error_text)
                        return ModelResponse(
                            content="",
                            model=self.config.name,
                            finish_reason="error",
                            elapsed_ms=(time.time() - start) * 1000,
                        )
                    
                    data = await resp.json()
        except Exception as e:
            self._total_errors += 1
            logger.error("DeepSeek API call failed: %s", e)
            return ModelResponse(
                content="",
                model=self.config.name,
                finish_reason="error",
                elapsed_ms=(time.time() - start) * 1000,
            )
        
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        usage = data.get("usage", {})
        
        content = message.get("content", "") or ""
        tool_calls = message.get("tool_calls", [])
        
        tokens_total = usage.get("total_tokens", 0)
        self._total_tokens += tokens_total
        
        return ModelResponse(
            content=content,
            model=self.config.name,
            tokens_prompt=usage.get("prompt_tokens", 0),
            tokens_completion=usage.get("completion_tokens", 0),
            total_tokens=tokens_total,
            finish_reason=choice.get("finish_reason", "stop"),
            tool_calls=tool_calls,
            elapsed_ms=(time.time() - start) * 1000,
            raw_response=data,
        )

"""
自定义模型适配器示例
====================
展示如何实现自定义模型适配器接入Hyper-Agent。
此示例接入 OpenAI API，可作为其他模型接入的模板。
"""
import asyncio
import os
from typing import Any, Dict, List, Optional

from hyper_agent_sdk.adapters.base import ModelAdapter, ModelResponse
from hyper_agent_sdk.types import ModelConfig, ToolDefinition
from hyper_agent_sdk.plugin_base import HyperAgentPlugin
from hyper_agent_sdk.types import PluginManifest, TaskRequest, TaskResponse


class CustomModelPlugin(HyperAgentPlugin):
    """
    自定义模型插件
    
    展示如何将自己训练的模型或第三方API接入Hyper-Agent。
    只需实现 ModelAdapter.chat() 方法即可。
    """
    
    def __init__(self):
        manifest = PluginManifest(
            plugin_id="custom-model",
            name="Custom Model Plugin",
            version="0.1.0",
            description="接入自定义模型的插件示例",
            author="Your Name",
            capabilities=["adapter", "model"],
        )
        super().__init__(manifest)
        self._adapter = None
    
    async def on_initialize(self) -> None:
        # 初始化自定义适配器
        config = ModelConfig(
            name="my-custom-model",
            provider="custom",
            api_key_env="CUSTOM_API_KEY",
            api_base="https://your-api-endpoint.com/v1",
            max_tokens=4096,
            temperature=0.7,
        )
        # self._adapter = MyCustomAdapter(config)
        pass
    
    async def on_shutdown(self) -> None:
        pass
    
    async def on_task_request(self, task: TaskRequest) -> TaskResponse:
        payload = task.payload
        messages = payload.get("messages", [
            {"role": "user", "content": payload.get("content", "")}
        ])
        
        # 调用自定义适配器
        # response = await self._adapter.chat(messages)
        
        return TaskResponse(
            task_id=task.task_id,
            success=True,
            result="Custom model response goes here",
            model_used="my-custom-model",
        )


def create_plugin():
    return CustomModelPlugin()

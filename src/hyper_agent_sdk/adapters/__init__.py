"""
模型适配器层
============
提供标准化的模型接入适配器基类与具体实现。
外部开发者可继承基类实现自定义模型接入。
"""
from hyper_agent_sdk.adapters.base import ModelAdapter, ModelResponse
from hyper_agent_sdk.adapters.deepseek import DeepSeekAdapter
from hyper_agent_sdk.adapters.glm import GLMAdapter

__all__ = ["ModelAdapter", "ModelResponse", "DeepSeekAdapter", "GLMAdapter"]

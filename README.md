# Hyper-Agent SDK

<div align="center">

**面向企业级AI应用的开源多智能体框架插件开发工具包**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange)](https://github.com/hyper-agent/sdk/releases)

</div>

---

## 概述

Hyper-Agent SDK 是 Hyper-Agent 多智能体 AI 框架的**官方开源插件开发工具包**。开发者可以基于此 SDK 为 Hyper-Agent 开发能力扩展插件，包括自定义模型适配器、向量数据库驱动、工具组件和工作流模板。

### 核心特性

| 特性 | 说明 |
|------|------|
| **插件基类** | 标准化的插件生命周期管理，连接内核API |
| **模型适配器** | 统一接入接口，支持 DeepSeek、GLM、OpenAI 及自定义模型 |
| **向量数据库** | 开箱即用的 ChromaDB 驱动，支持扩展其他向量数据库 |
| **内置工具** | Calculator、DateTime、JSON Parser 等常用工具组件 |
| **工作流模板** | 顺序执行、并行执行、条件分支三种执行模式 |
| **权限隔离** | SDK 仅暴露公开 API，内核调度逻辑完全隔离 |

---

## 快速开始

### 安装

```bash
pip install hyper-agent-sdk
```

### 5分钟写一个插件

```python
from hyper_agent_sdk import HyperAgentPlugin, PluginManifest, TaskRequest, TaskResponse

class MyPlugin(HyperAgentPlugin):
    def __init__(self):
        manifest = PluginManifest(
            plugin_id="my-plugin",
            name="My First Plugin",
            version="0.1.0",
            description="我的第一个 Hyper-Agent 插件",
            capabilities=["tool"],
        )
        super().__init__(manifest)
    
    async def on_initialize(self):
        print(f"{self.plugin_name} 已就绪")
    
    async def on_shutdown(self):
        print(f"{self.plugin_name} 已关闭")
    
    async def on_task_request(self, task: TaskRequest) -> TaskResponse:
        content = task.payload.get("content", "")
        
        # 通过公开 API 调用模型（实际部署时连接内核）
        result = await self.invoke_model(
            model_name="deepseek-v3",
            prompt=f"分析以下内容：\n{content}",
        )
        
        return TaskResponse(
            task_id=task.task_id,
            success=True,
            result=result.get("content", ""),
        )

# 插件入口点
def create_plugin():
    return MyPlugin()
```

### 使用模型适配器（独立使用）

```python
import asyncio
from hyper_agent_sdk.adapters import DeepSeekAdapter
from hyper_agent_sdk.types import ModelConfig

async def main():
    config = ModelConfig(
        name="deepseek-chat",
        provider="deepseek",
        api_key_env="DEEPSEEK_API_KEY",
        temperature=0.7,
    )
    adapter = DeepSeekAdapter(config)
    
    response = await adapter.chat([
        {"role": "user", "content": "什么是多智能体系统？"}
    ])
    print(response.content)

asyncio.run(main())
```

---

## 项目结构

```
hyper-agent-sdk/
├── src/hyper_agent_sdk/          # SDK 核心代码
│   ├── __init__.py               # 公开导出
│   ├── types.py                  # 通用类型定义
│   ├── plugin_base.py            # 插件基类
│   ├── adapters/                 # 模型适配器
│   │   ├── base.py               #   适配器基类
│   │   ├── deepseek.py           #   DeepSeek 适配器
│   │   └── glm.py                #   GLM 适配器
│   ├── drivers/                  # 向量数据库驱动
│   │   ├── base.py               #   驱动基类
│   │   └── chromadb.py           #   ChromaDB 驱动
│   ├── tools/                    # 工具组件
│   │   ├── base.py               #   工具基类
│   │   └── builtins.py           #   内置工具集
│   └── workflows/                # 工作流模板
│       └── template.py           #   模板定义
├── examples/                     # 示例代码
│   ├── hello_plugin/             #   Hello World 插件
│   └── custom_adapter/           #   自定义适配器
├── docs/                         # 文档
├── pyproject.toml                # 项目配置
└── README.md                     # 本文件
```

---

## API 概览

### 公开 API（插件可调用）

| API | 说明 | 权限 |
|-----|------|------|
| `task.submit` | 提交任务到智能体集群 | ✅ ALLOW |
| `memory.search` | 搜索历史摘要记忆 | ✅ ALLOW |
| `memory.add_message` | 写入记忆 | ✅ ALLOW |
| `model.invoke` | 调用指定模型 | ✅ ALLOW |
| `config.get` | 读取公开配置 | ✅ ALLOW |
| `event.subscribe` | 订阅系统事件 | ✅ ALLOW |

### 内核 API（插件不可访问）

| API | 说明 |
|-----|------|
| `scheduler.reroute` | 修改调度规则 |
| `auth.bypass` | 绕过权限检查 |
| `config.set_core` | 修改核心配置 |
| `memory.raw_access` | 直接访问原始日志 |
| `compressor.override` | 覆写压缩行为 |

> **安全声明**: 以上内核 API 仅在内核内部使用，SDK 无任何接口暴露这些能力。

---

## 进阶开发

### 自定义模型适配器

```python
from hyper_agent_sdk.adapters import ModelAdapter, ModelResponse
from hyper_agent_sdk.types import ModelConfig

class MyCustomAdapter(ModelAdapter):
    async def chat(self, messages, tools=None, **kwargs):
        # 实现你的 API 调用逻辑
        # ...
        return ModelResponse(
            content="模型返回的内容",
            model="my-model",
            total_tokens=100,
        )
```

### 自定义向量数据库驱动

```python
from hyper_agent_sdk.drivers import VectorDBDriver, SearchResult

class MyVectorDB(VectorDBDriver):
    def search(self, query_vector, top_k=5):
        # 实现你的向量检索逻辑
        results = my_db.search(query_vector, top_k)
        return [SearchResult(id=r.id, score=r.score, metadata=r.meta) for r in results]
    
    def insert(self, vectors, metadatas, ids):
        my_db.insert(vectors, metadatas, ids)
```

---

## 许可

本项目基于 **MIT License** 开源。

---

## 相关链接

- [快速上手文档](docs/quick-start.md)
- [插件开发指南](docs/plugin-dev-guide.md)
- [API 参考文档](docs/api-reference.md)
- [架构设计文档](../docs/architecture.md)

---

<div align="center">
  <sub>Built with ❤️ by the Hyper-Agent Team</sub>
</div>

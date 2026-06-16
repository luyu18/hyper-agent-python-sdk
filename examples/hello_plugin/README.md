# Hello Plugin 示例

最简单的 Hyper-Agent 插件示例。

## 文件结构

```
hello_plugin/
├── plugin.py        # 插件主文件
└── README.md        # 本文件
```

## 使用方式

```python
from hyper_agent_sdk import HyperAgentPlugin
from examples.hello_plugin.plugin import HelloPlugin

# 创建插件
plugin = HelloPlugin()

# 注册到内核
kernel = Kernel()
kernel.initialize()
kernel.register_plugin({
    "plugin_id": "hello-plugin",
    "name": "Hello Plugin",
    "version": "0.1.0",
    "capabilities": ["demo"],
    "entry_point": "hello_plugin.plugin:create_plugin",
})
```

"""
Hello Plugin 示例
=================
最简单的Hyper-Agent插件示例，展示插件的基本结构。
"""
import asyncio
from hyper_agent_sdk.plugin_base import HyperAgentPlugin
from hyper_agent_sdk.types import PluginManifest, TaskRequest, TaskResponse


class HelloPlugin(HyperAgentPlugin):
    """
    Hello World 示例插件
    
    功能:
    - 响应 "hello" 消息
    - 记录交互次数
    - 展示插件生命周期
    """
    
    def __init__(self):
        manifest = PluginManifest(
            plugin_id="hello-plugin",
            name="Hello Plugin",
            version="0.1.0",
            description="A simple Hello World plugin for Hyper-Agent",
            author="Hyper-Agent Team",
            capabilities=["demo", "tutorial"],
        )
        super().__init__(manifest)
        self._greet_count = 0
    
    async def on_initialize(self) -> None:
        print(f"[{self.plugin_name}] 初始化完成，准备接受请求。")
    
    async def on_shutdown(self) -> None:
        print(f"[{self.plugin_name}] 已关闭。共处理 {self._greet_count} 次问候。")
    
    async def on_task_request(self, task: TaskRequest) -> TaskResponse:
        """
        处理任务请求
        
        如果消息包含 "hello"，返回问候语。
        否则返回通用响应。
        """
        self._greet_count += 1
        content = task.payload.get("content", "")
        
        if "hello" in content.lower() or "你好" in content:
            response_text = (
                f"👋 Hello from Hyper-Agent! 这是第 {self._greet_count} 次问候。\n"
                f"你的消息: {content}\n"
                f"插件: {self.plugin_name} v{self.manifest.version}"
            )
        else:
            response_text = (
                f"HelloPlugin 收到你的消息: {content[:100]}\n"
                f"试试说 'hello' 看看？"
            )
        
        return TaskResponse(
            task_id=task.task_id,
            success=True,
            result=response_text,
            model_used="hello-plugin",
        )


# 插件入口点
def create_plugin():
    """插件工厂函数（由Hyper-Agent框架调用）"""
    return HelloPlugin()

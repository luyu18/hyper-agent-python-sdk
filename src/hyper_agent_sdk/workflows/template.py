"""
工作流模板
==========
预定义的业务工作流模式，开发者可继承或组合使用。
提供顺序、并行、条件分支等常见模式。
"""
from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from hyper_agent_sdk.types import WorkflowStep, TaskRequest, TaskResponse

logger = logging.getLogger("hyper_agent.workflow")


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowContext:
    """工作流上下文（步骤间数据传递）"""
    workflow_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    step_results: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        self.data[key] = value


class WorkflowTemplate(ABC):
    """
    工作流模板基类
    
    提供标准的工作流执行模式：
    - Sequential: 顺序执行
    - Parallel: 并行执行
    - Conditional: 条件分支
    
    使用示例:
        class MyWorkflow(WorkflowTemplate):
            def get_steps(self):
                return [
                    WorkflowStep(step_id="analyze", name="分析需求"),
                    WorkflowStep(step_id="generate", name="生成内容", depends_on=["analyze"]),
                    WorkflowStep(step_id="review", name="审核", depends_on=["generate"]),
                ]
            
            async def execute_step(self, step, context):
                # 实现步骤逻辑
                ...
    """
    
    def __init__(self, workflow_id: str, name: str = ""):
        self.workflow_id = workflow_id
        self.name = name
        self.status = WorkflowStatus.PENDING
        self._context = WorkflowContext(workflow_id=workflow_id)
    
    @abstractmethod
    def get_steps(self) -> List[WorkflowStep]:
        """定义工作流步骤"""
        ...
    
    @abstractmethod
    async def execute_step(
        self,
        step: WorkflowStep,
        context: WorkflowContext,
    ) -> TaskResponse:
        """执行单个步骤"""
        ...
    
    async def run(self) -> Dict[str, Any]:
        """执行工作流"""
        self.status = WorkflowStatus.RUNNING
        steps = self.get_steps()
        
        try:
            completed_steps: Dict[str, TaskResponse] = {}
            failed_steps: List[str] = []
            
            while len(completed_steps) + len(failed_steps) < len(steps):
                # 查找可执行步骤（依赖已满足）
                ready = self._get_ready_steps(steps, completed_steps, failed_steps)
                
                if not ready:
                    if failed_steps:
                        self.status = WorkflowStatus.FAILED
                        break
                    await asyncio.sleep(0.1)
                    continue
                
                for step in ready:
                    resp = await self.execute_step(step, self._context)
                    if resp.success:
                        completed_steps[step.step_id] = resp
                        self._context.step_results[step.step_id] = resp.result
                    else:
                        if step.retry_on_failure:
                            # 重试
                            resp = await self.execute_step(step, self._context)
                            if resp.success:
                                completed_steps[step.step_id] = resp
                                continue
                        failed_steps.append(step.step_id)
            
            if not failed_steps:
                self.status = WorkflowStatus.COMPLETED
            
            return {
                "workflow_id": self.workflow_id,
                "status": self.status.value,
                "completed_steps": list(completed_steps.keys()),
                "failed_steps": failed_steps,
                "context": self._context.data,
            }
        except Exception as e:
            self.status = WorkflowStatus.FAILED
            logger.error("Workflow %s failed: %s", self.workflow_id, e)
            return {
                "workflow_id": self.workflow_id,
                "status": "failed",
                "error": str(e),
            }
    
    def _get_ready_steps(
        self,
        steps: List[WorkflowStep],
        completed: Dict[str, Any],
        failed: List[str],
    ) -> List[WorkflowStep]:
        """获取依赖已满足的步骤"""
        ready = []
        for step in steps:
            if step.step_id in completed or step.step_id in failed:
                continue
            if all(dep in completed for dep in step.depends_on):
                ready.append(step)
        return ready

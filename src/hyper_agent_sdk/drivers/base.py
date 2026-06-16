"""
向量数据库驱动基类
==================
定义所有向量数据库驱动的标准接口。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SearchResult:
    """搜索结果"""
    entry_id: str
    score: float
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "score": self.score,
            "text": self.text[:200],
            "metadata": self.metadata,
        }


class VectorDBDriver(ABC):
    """
    向量数据库驱动基类
    
    子类需实现:
    - store(): 存储文本向量
    - search(): 语义搜索
    - delete(): 删除向量
    - count(): 向量数量
    
    实现示例:
        class MyVectorDB(VectorDBDriver):
            async def store(self, entry_id, text, metadata):
                # 生成embedding并存储
                ...
    """
    
    def __init__(self, collection_name: str = "hyper_agent"):
        self.collection_name = collection_name
    
    @abstractmethod
    async def store(
        self,
        entry_id: str,
        text: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """存储文本向量"""
        ...
    
    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int = 3,
        embedding: Optional[List[float]] = None,
    ) -> List[SearchResult]:
        """语义搜索"""
        ...
    
    @abstractmethod
    async def delete(self, entry_id: str) -> bool:
        """删除向量条目"""
        ...
    
    @abstractmethod
    async def count(self) -> int:
        """返回向量总数"""
        ...
    
    async def batch_store(
        self,
        entries: List[Dict[str, Any]],
    ) -> int:
        """
        批量存储（默认逐条存储，子类可覆写）
        
        Returns:
            成功存储数量
        """
        success = 0
        for entry in entries:
            if await self.store(
                entry_id=entry["entry_id"],
                text=entry["text"],
                metadata=entry.get("metadata"),
            ):
                success += 1
        return success
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            await self.count()
            return True
        except Exception:
            return False

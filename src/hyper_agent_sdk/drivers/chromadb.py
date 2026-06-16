"""
ChromaDB 向量数据库驱动
========================
接入开源向量数据库 ChromaDB。
ChromaDB提供本地/服务端两种模式，适合开发与生产环境。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from hyper_agent_sdk.drivers.base import VectorDBDriver, SearchResult

logger = logging.getLogger("hyper_agent.driver.chromadb")


class ChromaDBDriver(VectorDBDriver):
    """
    ChromaDB 向量数据库驱动
    
    安装依赖:
        pip install chromadb
    
    使用示例:
        driver = ChromaDBDriver(
            collection_name="hyper_agent_summaries",
            persist_directory="./chroma_data",
        )
        await driver.connect()
        await driver.store("id-1", "这是一段文本", metadata={"source": "test"})
        results = await driver.search("文本", top_k=3)
    """
    
    def __init__(
        self,
        collection_name: str = "hyper_agent",
        persist_directory: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        super().__init__(collection_name)
        self._persist_directory = persist_directory
        self._host = host
        self._port = port
        self._client = None
        self._collection = None
        self._embedding_fn = None
    
    async def connect(self, embedding_fn=None):
        """连接到ChromaDB"""
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            raise ImportError(
                "chromadb is required. Install with: pip install chromadb"
            )
        
        if self._host:
            self._client = chromadb.HttpClient(
                host=self._host,
                port=self._port or 8000,
            )
        else:
            self._client = chromadb.PersistentClient(
                path=self._persist_directory or "./chroma_data",
            )
        
        # 获取或创建集合
        try:
            self._collection = self._client.get_collection(self.collection_name)
        except Exception:
            self._collection = self._client.create_collection(self.collection_name)
        
        # 存储外部embedding函数（如果提供）
        self._embedding_fn = embedding_fn
        
        count = await self.count()
        logger.info(
            "ChromaDB connected: collection=%s, count=%d",
            self.collection_name, count
        )
    
    async def store(
        self,
        entry_id: str,
        text: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        if self._collection is None:
            raise RuntimeError("ChromaDB not connected. Call connect() first.")
        
        try:
            kwargs = {
                "ids": [entry_id],
                "documents": [text],
            }
            
            if embedding:
                kwargs["embeddings"] = [embedding]
            
            if metadata:
                # ChromaDB要求metadata值为字符串/数值/布尔
                clean_meta = {
                    k: str(v) if not isinstance(v, (int, float, bool, str)) else v
                    for k, v in metadata.items()
                }
                kwargs["metadatas"] = [clean_meta]
            
            self._collection.add(**kwargs)
            return True
        except Exception as e:
            logger.error("ChromaDB store error: %s", e)
            return False
    
    async def search(
        self,
        query: str,
        top_k: int = 3,
        embedding: Optional[List[float]] = None,
    ) -> List[SearchResult]:
        if self._collection is None:
            raise RuntimeError("ChromaDB not connected.")
        
        try:
            kwargs = {
                "query_texts": [query],
                "n_results": top_k,
            }
            
            if embedding:
                kwargs["query_embeddings"] = [embedding]
            
            results = self._collection.query(**kwargs)
            
            if not results or not results.get("ids") or not results["ids"][0]:
                return []
            
            search_results = []
            for i, doc_id in enumerate(results["ids"][0]):
                doc_text = results["documents"][0][i] if results.get("documents") else ""
                distance = results["distances"][0][i] if results.get("distances") else 0.0
                meta = results["metadatas"][0][i] if results.get("metadatas") else {}
                
                # 距离转相似度
                score = 1.0 / (1.0 + distance) if distance else 1.0
                
                search_results.append(SearchResult(
                    entry_id=doc_id,
                    score=round(score, 4),
                    text=doc_text,
                    metadata=meta,
                ))
            
            return search_results
        except Exception as e:
            logger.error("ChromaDB search error: %s", e)
            return []
    
    async def delete(self, entry_id: str) -> bool:
        if self._collection is None:
            return False
        try:
            self._collection.delete(ids=[entry_id])
            return True
        except Exception as e:
            logger.error("ChromaDB delete error: %s", e)
            return False
    
    async def count(self) -> int:
        if self._collection is None:
            return 0
        try:
            return self._collection.count()
        except Exception:
            return 0
    
    async def close(self):
        """关闭连接"""
        self._client = None
        self._collection = None
        logger.info("ChromaDB disconnected")

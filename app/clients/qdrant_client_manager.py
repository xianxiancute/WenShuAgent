import asyncio

from qdrant_client import QdrantClient, AsyncQdrantClient

from app.conf.app_config import QdrantConfig, app_config
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct

class QdrantClientManager:
    def __init__(self, config: QdrantConfig):
        self.client: AsyncQdrantClient | None =None
        self.config: QdrantConfig = config

   #获取配置地址
    def _get_url(self):
       return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        #初始化qdrant客户端
        self.client= AsyncQdrantClient(url=self._get_url())

    async def close(self):
        #关闭客户端
        await self.client.close()

qdrant_client_manager = QdrantClientManager(app_config.qdrant)

if __name__ == '__main__':
    qdrant_client_manager.init()
    client = qdrant_client_manager.client
    async def test():
        #创建集合
        await client.create_collection(
            collection_name="test_collection_async",
            vectors_config=VectorParams(size=4, distance=Distance.DOT),
        )

        #插入数据
        operation_info = await client.upsert(
            collection_name="test_collection_async",
            wait=True,
            points=[
                PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}),
                PointStruct(id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"city": "London"}),
                PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"city": "Moscow"}),
                PointStruct(id=4, vector=[0.18, 0.01, 0.85, 0.80], payload={"city": "New York"}),
                PointStruct(id=5, vector=[0.24, 0.18, 0.22, 0.44], payload={"city": "Beijing"}),
                PointStruct(id=6, vector=[0.35, 0.08, 0.11, 0.44], payload={"city": "Mumbai"}),
            ],
        )

        print(operation_info)

        #查询数据
        search_result = (await client.query_points(
            collection_name="test_collection_async",
            query=[0.2, 0.1, 0.9, 0.7],
            with_payload=False,
            limit=3
        )).points

        print(search_result)

        await qdrant_client_manager.client.close()

#asyncio.run(test())
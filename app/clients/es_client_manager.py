import asyncio
from typing import Optional

from elasticsearch import AsyncElasticsearch

from app.conf.app_config import ESConfig, app_config


class ESClientManager:
    def __init__(self, config: ESConfig):
        self.config = config
        self.client: Optional[AsyncElasticsearch] | None = None

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = AsyncElasticsearch(hosts= self._get_url())

    async def close(self):
        await self.client.close()


es_client_manager = ESClientManager(app_config.es)

if __name__ == '__main__':
   #测试
   es_client_manager.init()
   client = es_client_manager.client
   async def test():
       #创建索引
       # await client.indices.create(
       #     index="books"
       # )
       #写入数据
       await client.index(
           index="books",
           document={
               "name":" Snow Crash",
               "author": "112",
               "release_data":"1992-3-3",
               "page_count":470
           }
       )
       #查询数据
       resp = await client.search(
           index="books"
       )
       print(resp)

       await client.close()


   asyncio.run(test())
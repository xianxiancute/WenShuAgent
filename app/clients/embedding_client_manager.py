# import asyncio
# from typing import Optional
#
# from langchain_huggingface import HuggingFaceEndpointEmbeddings
#
# from app.conf.app_config import EmbeddingConfig, app_config
#
# class EmbeddingClientManager:
#     def __init__(self, config: EmbeddingConfig):
#         self.client: Optional[HuggingFaceEndpointEmbeddings] = None
#         self.config = config
#
#     def _get_url(self):
#         return f"http://{self.config.host}:{self.config.port}"
#
#     def init(self):
#         self.client = HuggingFaceEndpointEmbeddings(model=self._get_url())
#
# embedding_client_manager = EmbeddingClientManager(app_config.embedding)
#
#
# # from langchain_huggingface import HuggingFaceEndpointEmbeddings
# # import inspect
# # print(inspect.signature(HuggingFaceEndpointEmbeddings.__init__))
# #测试
# if __name__ == '__main__':
#     #初始化
#     embedding_client_manager.init()
#     client= embedding_client_manager.client
#     # text = "What is deep learning?"
#     # query_result = client.embed_query(text)
#     # print(query_result[:3])
#     async def test():
#         text = "What is deep learning?"
#         query_result = await client.aembed_query(text)
#         compile(query_result[:3])
#
#     asyncio.run(test())

import requests
import aiohttp
import asyncio
from typing import List
from langchain_core.embeddings import Embeddings
import logging

logger = logging.getLogger(__name__)


class TEIEmbeddingClient(Embeddings):
    """专门用于连接本地 TEI 服务的 Embedding 客户端"""

    def __init__(self, base_url: str = "http://localhost:8081"):
        self.base_url = base_url
        # TEI 服务的标准嵌入端点
        self.embed_endpoint = f"{base_url}/embed"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """为文档列表生成嵌入向量（同步方法）"""
        try:
            response = requests.post(
                self.embed_endpoint,
                json={"inputs": texts},  # TEI 标准请求格式
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            response.raise_for_status()
            return response.json()  # TEI 直接返回向量列表
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"TEI 服务请求失败: {e}") from e

    def embed_query(self, text: str) -> List[float]:
        """为单个查询文本生成嵌入向量（同步方法）"""
        return self.embed_documents([text])[0]

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """为文档列表生成嵌入向量（异步方法，支持批量处理）"""
        if not texts:
            return []

        # 分批处理，每批50条
        batch_size = 10
        all_embeddings = []

        # 创建连接池和会话
        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=5,
            ttl_dns_cache=300
        )
        timeout = aiohttp.ClientTimeout(total=120, connect=30, sock_read=60)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                try:
                    async with session.post(
                            self.embed_endpoint,
                            json={"inputs": batch},
                            headers={"Content-Type": "application/json"}
                    ) as response:
                        response.raise_for_status()
                        result = await response.json()

                        # 处理返回结果
                        if isinstance(result, list):
                            # TEI 返回向量列表
                            all_embeddings.extend(result)
                        elif isinstance(result, dict) and 'embeddings' in result:
                            # 某些版本返回字典格式
                            all_embeddings.extend(result['embeddings'])
                        else:
                            # 单个向量
                            all_embeddings.append(result)

                    # 批次间添加小延迟，避免压垮服务
                    if i + batch_size < len(texts):
                        await asyncio.sleep(0.1)

                except aiohttp.ClientError as e:
                    logger.error(f"TEI 服务异步请求失败 (批次 {i // batch_size + 1}): {e}")
                    raise RuntimeError(f"TEI 服务异步请求失败: {e}") from e
                except Exception as e:
                    logger.error(f"处理批次时发生未知错误: {e}")
                    raise

        return all_embeddings

    async def aembed_query(self, text: str) -> List[float]:
        """为单个查询文本生成嵌入向量（异步方法）"""
        if not text:
            return []
        result = await self.aembed_documents([text])
        return result[0] if result else []


from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddingClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.client: TEIEmbeddingClient | None = None

    def _get_url(self) -> str:
        # 确保使用 127.0.0.1 避免 DNS 解析问题
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        url = self._get_url()
        self.client = TEIEmbeddingClient(url)
        print(f"✅ 客户端已成功连接到: {url}")


# 初始化
embedding_client_manager = EmbeddingClientManager(app_config.embedding)

if __name__ == '__main__':
    embedding_client_manager.init()
    client = embedding_client_manager.client

    text = "什么是深度学习？"
    try:
        query_result = client.embed_query(text)
        print(f"✅ 查询成功！向量维度: {len(query_result)}")
        print(f"前5个维度: {query_result[:5]}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")


    # 异步测试
    async def test_async():
        try:
            # 测试单个查询
            query_result_async = await client.aembed_query(text)
            print(f"✅ 异步查询成功！向量维度: {len(query_result_async)}")
            print(f"前5个维度: {query_result_async[:5]}")

            # 测试批量查询
            texts = ['region_id', '地区唯一标识。', '地区ID', '区域ID', 'province', '订单所属的省份名称。', '省份', '省', '所在省份', 'region_name', '订单所属的大区名称，如华东、华南等。', '地区', '区域', '大区', 'country', '地区所属国家名称。', '国家', '国家名称', 'customer_id', '客户唯一标识。', '客户ID', '用户ID', 'customer_name', '客户名称。', '客户名称', '用户名 称', 'gender', '客户性别。', '性别', 'member_level', '客户会员等级。', '会员等级', '用户等级', 'product_id', '商品唯一标识。', '商品ID', '产品ID', 'product_name', '商品名称。', '商品名称', '产品名称', 'category', '商品所属品类。', '商品类别', '品类', '分类', 'brand', '商品品牌名称。', '品牌', '品牌名称', 'date_id', '日期唯一标识，格式 yyyyMMdd。', '日期ID', '日期', 'year', '年份。', '年', '年份', 'quarter', '季度。', '季度', 'month', '月份。', '月', '月份', 'day', '日。', '日', '天', 'order_id', '订单唯一标识。', '订单ID', 'customer_id', '关联客户维度的外键。', '客户ID', '用户ID', 'product_id', '关联商品维度的外键。', '商品ID', '产品ID', 'date_id', '关联时间维度的外键。', '日期', '下单日期', 'region_id', '关联 地区维度的外键。', '地区ID', '区域ID', 'order_quantity', '订单中商品的购买数量。', '销量', '购买数量', '件数', 'order_amount', '订单金额。', '销售额', '订单金额', '收入']
            batch_results = await client.aembed_documents(texts)
            print(f"✅ 批量查询成功！返回 {len(batch_results)} 个向量")
            for i, emb in enumerate(batch_results):
                print(f"  文本{i + 1} 向量维度: {len(emb)}")

        except Exception as e:
            print(f"❌ 异步测试失败: {e}")


    # 运行异步测试
    #asyncio.run(test_async())
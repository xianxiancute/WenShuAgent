from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.entities.column_info import ColumnInfo
from app.prompt.prompt_loader import load_prompt
from app.core.log import logger


async def recall_column(state:DataAgentState, runtime:Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step":"召回列信息", "status": "running"})

    try:
        query = state["query"]
        keywords = state["keywords"]

        column_qdrant_repository = runtime.context["column_qdrant_repository"]
        embedding_client = runtime.context["embedding_client"]

        #借助大模型扩展关键字
        #chain = prompt | llm | output_parser
        prompt = PromptTemplate(template=load_prompt("extend_keywords_for_column_recall"), input_variables=['query'])
        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser

        result = await chain.ainvoke({"query": query})
        keywords = set(keywords + result)

        #从向量数据库检索字段信息

        column_info_map:dict[str, ColumnInfo] = {}
        for keyword in keywords:
            embedding = await embedding_client.aembed_query(keyword)
            current_column_infos:list[ColumnInfo] = await column_qdrant_repository.search(embedding, score_threshold=0.6, limit= 10)
            for column_info in current_column_infos:
                if column_info.id not in column_info_map:
                    column_info_map[column_info.id] = column_info
        retrieved_column_infos:list[ColumnInfo]=list(column_info_map.values())

        logger.info(f"召回字段信息: {list(column_info_map.keys())}")
        writer({"type": "progress", "step": "召回列信息", "status": "success"})
        return {"retrieved_column_infos": retrieved_column_infos}
    except Exception as e:
        logger.error(f"召回列信息出错: {e}")
        writer({"type": "progress", "step": "召回列信息", "status": "error"})
        raise
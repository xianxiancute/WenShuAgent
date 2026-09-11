from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def run_sql(state:DataAgentState, runtime:Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step":"执行sql", "status": "running"})

    try:
        sql = state["sql"]
        dw_mysql_repository = runtime.context["dw_mysql_repository"]

        result = await dw_mysql_repository.run(sql)

        logger.info(f"sql执行结果：{result}")
        writer({"type": "progress", "step": "执行sql", "status": "success"})
        writer({"type": "result", "data": result})
    except Exception as e:
        logger.error(f"执行sql出错: {e}")
        writer({"type": "progress", "step": "执行sql", "status": "error"})
        raise
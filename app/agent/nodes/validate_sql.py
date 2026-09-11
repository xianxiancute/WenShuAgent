from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.repositories.mysql.dw.dw_mysql_repositories import DWMySQLRepository
from app.core.log import logger


async def validate_sql(state:DataAgentState, runtime:Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step":"校验sql", "status": "running"})

    try:
        sql = state["sql"]

        dw_mysql_repository: DWMySQLRepository = runtime.context["dw_mysql_repository"]

        try:
            await dw_mysql_repository.validate_sql(sql)
            logger.info("sql校验成功,语法正确")
            writer({"type": "progress", "step": "校验sql", "status": "success"})
            return {"error": None}
        except Exception as e:
            logger.info(f"sql校验失败,语法错误: {str(e)}")
            writer({"type": "progress", "step": "校验sql", "status": "success"})
            return {"error": str(e)}
    except Exception as e:
        logger.error(f"校验sql出错: {e}")
        writer({"type": "progress", "step": "校验sql", "status": "error"})
        raise

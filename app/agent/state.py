from typing import TypedDict

from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.value_info import ValueInfo

class MetricInfoState(TypedDict):
    name:str
    description:str
    relevant_columns: list[str]
    alias: list[str]

class ColumnInfoState(TypedDict):
    name:str
    type:str
    role:str
    examples: list
    description:str
    alias: list[str]


class TableInfoState(TypedDict):
    name:str
    role:str
    description:str
    columns: list[ColumnInfoState]

class DateInfoState(TypedDict):
    date: str
    weekday: str
    quarter: str

class DBInfoState(TypedDict):
    version: str
    dialect: str


class DataAgentState(TypedDict):

    query: str  #用户的输入查询
    keywords: str #抽取的关键字
    retrieved_column_infos: list[ColumnInfo] #检索到的字段信息
    retrieved_metric_infos: list[MetricInfo] #检索到的指标信息
    retrieved_value_infos: list[ValueInfo] #检索到的值信息

    table_infos: list[TableInfoState]
    metric_infos: list[MetricInfoState]

    date_info: DateInfoState#日期信息
    db_info: DBInfoState#数据库信息

    sql: str#生成的sql

    error: str  #校验sql时的报错信息
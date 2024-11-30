from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    code: int = 200
    data: Optional[T]
    msg: str = "success"


class QueryData(BaseModel):
    """分页查询基础数据"""

    offset: int = Field(default=1, description="页码", ge=1)
    limit: int = Field(default=10, description="数量", ge=1)


class ListData(BaseModel, Generic[T]):
    """查列表时的模型"""

    total: int = Field(..., description="总数")
    items: T = Field(..., description="数据列表")
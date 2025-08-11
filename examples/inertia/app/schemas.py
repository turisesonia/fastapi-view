from pydantic import BaseModel
from typing import Any


class BaseResponseModel(BaseModel):
    """基礎回應模型"""
    success: bool = True
    message: str | None = None
    data: Any | None = None


class PaginationModel(BaseModel):
    """分頁模型"""
    page: int = 1
    per_page: int = 10
    total: int = 0
    pages: int = 0


class PaginatedResponseModel(BaseResponseModel):
    """分頁回應模型"""
    pagination: PaginationModel | None = None


class FeatureModel(BaseModel):
    """功能特色模型"""
    title: str
    description: str
    icon: str | None = None
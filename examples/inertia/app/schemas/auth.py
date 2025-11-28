from pydantic import BaseModel


class LoginRequest(BaseModel):
    """登入表單資料"""
    username: str
    password: str


class User(BaseModel):
    """用戶資料模型"""
    id: int
    username: str
    display_name: str
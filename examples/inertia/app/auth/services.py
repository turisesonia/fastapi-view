# 模擬用戶資料庫
MOCK_USERS = {
    "admin": {
        "id": 1,
        "username": "admin",
        "password": "password",
        "display_name": "管理員",
    },
    "user": {
        "id": 2,
        "username": "user",
        "password": "password",
        "display_name": "一般使用者",
    },
}


class AuthService:
    def authenticate_user(self, username: str, password: str) -> dict | None:
        user_data = MOCK_USERS.get(username)
        if user_data and user_data["password"] == password:
            # 返回用戶資料 (不包含密碼)
            return {
                "id": user_data["id"],
                "username": user_data["username"],
                "display_name": user_data["display_name"],
            }

        return None

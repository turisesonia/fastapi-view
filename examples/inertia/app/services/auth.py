MOCK_USERS = {
    "admin": {
        "id": 1,
        "username": "admin",
        "password": "password",
        "display_name": "Admin",
    },
    "user": {
        "id": 2,
        "username": "user",
        "password": "password",
        "display_name": "User",
    },
}


class AuthService:
    def authenticate(self, username: str, password: str) -> dict | None:
        user_data = MOCK_USERS.get(username)

        if user_data and user_data["password"] == password:
            return {
                "id": user_data["id"],
                "username": user_data["username"],
                "display_name": user_data["display_name"],
            }

        return None

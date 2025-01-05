class employee_not_found(Exception):
    def __init__(self):
        self.message = "employee not found "
        super().__init__(self.message)

class user_already_exist(Exception):
    def __init__(self, message: str = "Already exist") -> None:
        self.message = message
        super().__init__(self.message)


class token_expired(Exception):
    def __init__(self):
        self.message = "Token expired "
        super().__init__(self.message)

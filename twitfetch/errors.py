class InvalidLoginError(Exception):
    def __init__(self, message: str = 'invalid login info'):
        super().__init__(message)
        self.error_code = 404
        self.additional_data = "invalid username or password"
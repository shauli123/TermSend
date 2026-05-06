# User errors - errors related to users (login/register/token)
class UserError(Exception):
    def __init__(self, message):
        super().__init__(message)

class UserAlreadyExists(UserError):
    def __init__(self, message):
        super().__init__(message)
        
class UserDoesntExist(UserError):
    def __init__(self, message):
        super().__init__(message)
        
class InvalidCredentials(UserError):
    def __init__(self, message):
        super().__init__(message)

class TokenError(UserError):
    def __init__(self, message):
        super().__init__(message)


# Enum Errors
class UnsupportedCommand(Exception):
    def __init__(self, message):
        super().__init__(message)

class UnsupportedStatusCode(Exception):
    def __init__(self, message):
        super().__init__(message)

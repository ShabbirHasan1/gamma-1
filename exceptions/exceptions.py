class InvalidMethodException(Exception):
    def __init__(self, message):
        super().__init__(f"Specified method: {str(message)} not found. Please refer to documentation.")

class UncallableMethodException(Exception):
    def __init__(self, message):
        super().__init__(f"Specified method: {str(message)} is uncallable.")

class NoDataException(Exception):
    def __init__(self):
        super().__init__("No data found to parse.")

class KeyNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f"Key {str(message)} not found. Please refer to documentation.")

class InvalidDataTypeException(Exception):
    def __init__(self, message):
        super().__init__(f"Data type: {str(message)} is invalid. Please refer to documentation.")

class LoginFailedException(Exception):
    def __init__(self):
        super().__init__("Login failed! Please verify your credentials")

class MarketClosedException(Exception):
    def __init__(self, message):
        super().__init__(f"function {str(message)} is suppose to run during market hours.")

class NoDataException(Exception):
    def __init__(self):
        super().__init__("No data provided for it to process.")

class EngineNotStartedException(Exception):
    def __init__(self):
        super().__init__("You need to start the engine first.")

class NoSymbolException(Exception):
    def __init__(self):
        super().__init__("No symbols provided.")

class NotDefinedException(Exception):
    def __init__(self, message):
        super().__init__(f"Keyword {str(message)} is not defined")

class InvalidImplementationException(Exception):
    def __init__(self, message):
        super().__init__(message)
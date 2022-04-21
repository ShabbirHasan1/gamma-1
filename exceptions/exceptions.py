class InvalidMethodException(Exception):
    def __init__(self, message):
        super().__init__("Specified method: '"+str(message)+"' not found. Please refer to documentation.")

class UncallableMethodException(Exception):
    def __init__(self, message):
        super().__init__("Specified method: '"+str(message)+"' is uncallable.")

class NoDataException(Exception):
    def __init__(self):
        super().__init__("No data found to parse.")

class KeyNotFoundException(Exception):
    def __init__(self, message):
        super().__init__("Key '"+str(message)+"' not found. Please refer to documentation.")

class InvalidDataTypeException(Exception):
    def __init__(self, message):
        super().__init__("Data type: '"+str(message)+"' is invalid. Please refer to documentation.")

class LoginFailedException(Exception):
    def __init__(self):
        super().__init__("Login failed! Please verify your credentials")
class CorruptedMessageError(Exception):
    def __init__(self, error, innerException = None):
        Exception.__init__(self, error)
        self.innerException = innerException


class InvalidValueError(Exception):
    def __init__(self, error, innerException = None):
        Exception.__init__(self, error)
        self.innerException = innerException

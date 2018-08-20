class CorruptedMessageError(Exception):
    def __init__(self, error, inner_exception=None):
        Exception.__init__(self, error)
        self.inner_exception = inner_exception


class InvalidValueError(Exception):
    def __init__(self, error, inner_exception=None):
        Exception.__init__(self, error)
        self.inner_exception = inner_exception

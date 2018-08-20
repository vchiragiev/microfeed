from enums import ErrorEnum


class ErrorsDictionary:

    @classmethod
    def init(cls):
        cls.__errors_dict__ = \
            {
                ErrorEnum.CorruptedMessage: list(),
                ErrorEnum.InvalidValue: list(),
                ErrorEnum.DuplicateOrder: list(),
                ErrorEnum.MissingTrade: list(),
                ErrorEnum.RemoveWithNoOrder: list(),
                ErrorEnum.TradeWithNoOrder: list(),
            }

    @classmethod
    def add(cls, error_enum, error_message):
        cls.__errors_dict__[error_enum].append(error_message)

    @classmethod
    def print(cls):
        print(">>> Errors <<<")
        for key in cls.__errors_dict__:
            for error in cls.__errors_dict__[key]:
                print(str.format("{}:{}",key, error))

from enums import ErrorEnum
from typing import Dict, List


class ErrorsDictionary:

    def __init__(self):
        self.__errors_dict__: Dict[ErrorEnum, List] = \
            {
                ErrorEnum.CorruptedMessage: list(),
                ErrorEnum.InvalidValue: list(),
                ErrorEnum.DuplicateOrder: list(),
                ErrorEnum.MissingTrade: list(),
                ErrorEnum.RemoveWithNoOrder: list(),
                ErrorEnum.TradeWithNoOrder: list(),
            }

    def add(self, error_enum, error_message):
        self.__errors_dict__[error_enum].append(error_message)

    def print(self):
        print(">>> Errors <<<")
        for key in self.__errors_dict__:
            for error in self.__errors_dict__[key]:
                print(str.format("{}:{}", key, error))

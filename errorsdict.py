from enums import ErrorEnum
from typing import Dict, List


class ErrorsDictionary:

    def __init__(self):
        self._errors_dict: Dict[ErrorEnum, List] = \
            {
                ErrorEnum.CorruptedMessage: list(),
                ErrorEnum.InvalidValue: list(),
                ErrorEnum.DuplicateOrder: list(),
                ErrorEnum.MissingTrade: list(),
                ErrorEnum.RemoveWithNoOrder: list(),
                ErrorEnum.TradeWithNoOrder: list(),
            }

    def add(self, error_enum, error_message):
        self._errors_dict[error_enum].append(error_message)

    def print(self):
        for key in self._errors_dict:
            for error in self._errors_dict[key]:
                print(str.format("{}:{}", key, error))

from typing import List
from exceptions import CorruptedMessageError, InvalidValueError
import config


class Trade:
    # TODO: encapsulate properties ("private" or "readonly")
    def __init__(self, qty: int, price: float):
        self.qty = qty
        self.price = price

    @classmethod
    def parse(cls, values: List):
        if len(values) != 2:
            raise CorruptedMessageError("Unexpected number of values")

        try:
            quantity = int(values[0])
            price = float(values[1])
        except Exception as ex:
            raise InvalidValueError("Invalid value", ex)

        if quantity <= 0:
            raise InvalidValueError("Invalid qty: " + str(quantity))

        if config.MIN_PRICE_THRESHOLD >= price or price >= config.MAX_PRICE_THRESHOLD:
            raise InvalidValueError("Invalid price: " + str(price))

        return cls(quantity, price)

    def to_string(self):
        return str.format("qty={} price={}", self.qty, self.price)

    def __eq__(self, other):
        if isinstance(other, Trade):
            return self.qty == other.qty and self.price == other.price
        return False

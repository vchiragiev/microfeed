from enums import SideEnum
from exceptions import CorruptedMessageError, InvalidValueError
from typing import List
import config


class Order:
    # TODO: encapsulate properties ("private" or "readonly")
    def __init__(self, order_id: int, side: SideEnum, qty: int, price: float):

        #  if MAX_PRICE >= price <= MIN_PRICE:
        #  raise InvalidValueError("Invalid price: " + str(self.price))
        #  from main import MAX_PRICE, MIN_PRICE

        self.order_id = order_id
        self.side = side
        self.qty = qty
        self.price = price

    @classmethod
    def from_list(cls, values: List):
        if len(values) != 4:
            raise CorruptedMessageError("Unexpected number of values")
        try:
            order_id = int(values[0])
            side = SideEnum[values[1]]
            quantity = int(values[2])
            price = float(values[3])
        except Exception as ex:
            raise InvalidValueError("Invalid value", ex)

        if order_id <= 0:
            raise InvalidValueError("Invalid orderId: " + str(order_id))

        if quantity <= 0:
            raise InvalidValueError("Invalid qty: " + str(quantity))

        if config.MIN_PRICE_THRESHOLD >= price or price >= config.MAX_PRICE_THRESHOLD:
            raise InvalidValueError("Invalid price: " + str(price))

        return cls(order_id, side, quantity, price)

    def to_string(self):
        return str.format("orderId={} side={} qty={} price={}",
                          self.order_id, self.side, self.qty, self.price)

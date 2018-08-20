from enums import SideEnum, ActionEnum
from exceptions import CorruptedMessageError, InvalidValueError


class Order:
    def __init__(self, order_id: int, side: SideEnum, quantity: int, price: float):
        self.order_id = order_id
        self.side = side
        self.quantity = quantity
        self.price = price

    def __init__(self, values):
        if len(values) != 4:
            raise CorruptedMessageError("Unexpected number of values")

        try:
            self.order_id = int(values[0])
            self.side = SideEnum[values[1]]
            self.quantity = int(values[2])
            self.price = float(values[3])
        except Exception as ex:
            raise InvalidValueError("Invalid value", ex)

        if self.order_id <= 0:
            raise InvalidValueError("Invalid orderId: " + str(self.order_id))

        if self.quantity <= 0:
            raise InvalidValueError("Invalid quantity: " + str(self.quantity))

        if self.price <= 0:
            raise InvalidValueError("Invalid price: " + str(self.price))

    def clone(self):
        return Order(self.order_id, self.side, self.quantity, self.price)

    def to_string(self):
        return str.format("orderId={} side={} quantity={} price={}", self.order_id, self.side, self.quantity, self.price)


class OrderMessage:

    def __init__(self, action: ActionEnum, order: Order):
        self.action = action
        self.order = order

    def __init__(self, action: ActionEnum, values: str):
        self.action = action
        self.order = Order(values)

    def to_string(self):
        return str.format("action={} [order={}]", self.action, self.order.to_string())


from exceptions import CorruptedMessageError, InvalidValueError


class Trade:

    def __init__(self, quantity, price):
        self.quantity = quantity
        self.price = price

    def __init__(self, values):
        if len(values) != 2:
            raise CorruptedMessageError("Unexpected number of values")

        try:
            self.quantity = int(values[0])
            self.price = float(values[1])
        except Exception as ex:
            raise InvalidValueError("Invalid value", ex)

        if self.quantity <= 0:
            raise InvalidValueError("Invalid quantity: " + str(self.quantity))

        if self.price <= 0:
            raise InvalidValueError("Invalid price: " + str(self.price))

    def to_string(self):
        return str.format("quantity={} price={}", self.quantity, self.price)


class TradeMessage:

    def __init__(self, action, quantity, price):
        self.action = action
        self.trade = Trade(quantity, price)

    def __init__(self, action, values):
        self.action = action
        self.trade = Trade(values)

    def to_string(self):
        return str.format("action={} [trade={}]", self.action, self.trade.to_string())

from enums import ErrorEnum, ActionEnum
from exceptions import CorruptedMessageError, InvalidValueError
from order import OrderMessage, Order
from trade import TradeMessage, Trade
from errorsdict import ErrorsDictionary
from btree import Tree
from enums import SideEnum


class FeedHandler:
    def __init__(self):
        self.messages = list()
        self.orders_by_id: dict[int, Order] = dict()
        self.s_orders_by_price = Tree(0)  # add an artificial head with ZERO price.
        self.b_orders_by_price = Tree(0)  # The tree.right node will actually be the head
        self.expected_trades: [Trade] = []
        self.expected_orders: [int, int] = dict()

    def process_matched_orders(self, new_order: Order, matched_order_node: Tree):
        matched_order = matched_order_node.orders[0]

        # new_order.qty matches matched_order.qty
        # 1. register expected messages: trade, new_order(X), matched_order(X)
        # 2. remove matched_order from the book
        # 3. remove the node from the tree if no more orders with the same price
        # new_order fully filled nothing else to do
        if new_order.quantity == matched_order.quantity:
            self.expected_trades.append(TradeMessage(ActionEnum.T, matched_order.quantity, matched_order.price))
            self.expected_orders[new_order.order_id] = OrderMessage(ActionEnum.X, new_order.clone())
            self.expected_orders[matched_order.order_id] = OrderMessage(ActionEnum.X, matched_order.clone())
            new_order.quantity = 0
            matched_order_node.orders.pop(0)
            if len(matched_order_node.orders) == 0:
                matched_order_node.remove_me()

        # new_order.qty < matched_order.qty
        # 1. decrease matched_order.qty
        # 2. register expected messages: trade, new_order(X), matched_order(M)
        # new_order fully filled nothing else to do
        elif new_order.quantity < matched_order.quantity:
            matched_order.quantity = matched_order.quantity - new_order.quantity
            self.expected_trades.append(TradeMessage(ActionEnum.T, new_order.quantity, matched_order.price))
            self.expected_orders[new_order.order_id] = OrderMessage(ActionEnum.X, new_order.clone())
            # self.expected_orders[matched_order.order_id] = OrderMessage(ActionEnum.M, matched_order.clone())
            new_order.quantity = 0

        # new_order.qty < matched_order.qty
        # 1. decrease new_order.qty
        # 2. register expected messages: trade, new_order(M), matched_order(X)
        # 3. remove matched_order from the book
        # 4. remove the node from the tree if no more orders with the same price
        #    otherwise recursive call to try to fill the rest of qty
        else:
            new_order.quantity = new_order.quantity - matched_order.quantity
            self.expected_trades.append(TradeMessage(ActionEnum.T, matched_order.quantity, matched_order.price))
            self.expected_orders[new_order.order_id] = OrderMessage(ActionEnum.M, new_order.clone())
            # self.expected_orders[matched_order.order_id] = OrderMessage(ActionEnum.X, matched_order.clone())
            matched_order_node.orders.pop(0)
            if len(matched_order_node.orders) == 0:
                matched_order_node.remove_me()
            else:
                self.process_matched_orders(new_order, matched_order_node)

    def process_sell_order(self, s_order: Order):
        b_order_node = self.b_orders_by_price.right.find_rightmost_node()

        # s_order.price > than best b_order.price (no match)
        # add s_order to the book
        if s_order.price > b_order_node.price:
            self.s_orders_by_price.insert(s_order.price, s_order)
            self.orders_by_id[s_order.order_id] = s_order

        # best b_order.price >= s_order.price (yes match)
        # try to fill
        else:
            self.process_matched_orders(s_order, b_order_node)
            if s_order.quantity > 0:
                # try to fill again : recursive call
                self.process_sell_order(s_order)

    def process_buy_order(self, b_order: Order):
        s_order_node = self.s_orders_by_price.right.find_leftmost_node()

        # b_order.price < than best s_order.price (no match)
        # add b_order to the book
        if b_order.price < s_order_node.price:
            self.s_orders_by_price.insert(b_order.price, b_order)
            self.orders_by_id[b_order.order_id] = b_order

        # best b_order.price >= b_order.price (yes match)
        # try to fill
        else:
            self.process_matched_orders(b_order, s_order_node)
            if b_order.quantity > 0:
                # try to fill again : recursive call
                self.process_buy_order(b_order)

    def process_trade_message(self, trade_message: TradeMessage):
        while len(self.expected_trades) > 0:
            if trade_message.trade == self.expected_trades.pop(0):
                # found the expected trade.
                return

        # the trade was not found. report a TradeWithNoOrder error
        ErrorsDictionary.add(ErrorEnum.TradeWithNoOrder, trade_message.trade.to_string())

    def process_order_message(self, order_message: OrderMessage):
        return

    def process_message(self, values):
        action_str = list.pop(values, 0)
        try:
            action = ActionEnum[action_str]
            if action == ActionEnum.T:
                msg = TradeMessage(action, values)
                self.process_trade(msg.trade)
            else:
                msg = OrderMessage(action, values)
                self.messages.append(msg)
                if msg.order.side == SideEnum.S:

                    self.s_orders_by_price.insert(msg.order.price, msg.order)
                else: # Buy
                    self.b_orders_by_price.insert(msg.order.price, msg.order)
        except KeyError as er:
            ErrorsDictionary.add(ErrorEnum.CorruptedMessage, self.format_error(action_str, values, "Invalid Action"))
        except CorruptedMessageError as er:
            ErrorsDictionary.add(ErrorEnum.CorruptedMessage, self.format_error(action_str, values, er))
        except InvalidValueError as er:
            ErrorsDictionary.add(ErrorEnum.InvalidValue, self.format_error(action_str, values, er))

    def print_book(self):
        print(">>> Book <<<")
        self.s_orders_by_price.right.travers_reverse(lambda node: self.print_node("S", node))
        print("---")
        self.b_orders_by_price.right.travers(lambda node: self.print_node("B", node))

    @staticmethod
    def format_error(action, body, error):
        return str.format("Action:[{}] Body{} Error[{}]", action, body, error)

    @staticmethod
    def print_node(side, node: Tree):
        quantities = ",".join(side + str(order.quantity) for order in node.orders)
        print(node.price, "")

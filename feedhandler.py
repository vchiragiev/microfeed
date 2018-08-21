from typing import Set, Deque, Dict, List
from collections import deque
from enums import ErrorEnum, ActionEnum
from exceptions import CorruptedMessageError, InvalidValueError
from order import Order
from trade import Trade
from errorsdict import ErrorsDictionary
from btree import Tree
from enums import SideEnum
import config


class FeedHandler:
    def __init__(self):
        self._orders_by_id: Dict[int, Order] = dict()
        self._s_orders_by_price: Tree = Tree(config.MAX_PRICE_THRESHOLD)  # add an artificial root.
        self._b_orders_by_price: Tree = Tree(config.MIN_PRICE_THRESHOLD)  # add an artificial root.
        self._expected_trades: Deque[Trade] = deque()     # expected trades when new orders coming in
        self._expected_x_orders: Set[int] = set()         # orders to be deleted as result of expected trades
        self._errors = ErrorsDictionary()
        self._recent_trade_price: float = config.MAX_PRICE_THRESHOLD
        self._recent_trade_qty: int = 0

    def _process_matched_orders(self, new_order: Order, matched_order_node: Tree):
        matched_order = matched_order_node.orders[0]

        # if new_order.qty matches matched_order.qty
        # 1. register expected: trade, new_order(X), matched_order(X)
        # 2. remove matched_order from the book
        # 3. remove the node from the tree if no more orders with same price
        # new_order fully filled nothing else to do
        if new_order.qty == matched_order.qty:
            self._expected_trades.append(Trade(matched_order.qty, matched_order.price))  # add expected Trade
            self._expected_x_orders.add(new_order.order_id)                    # add expected new_order(X)
            self._expected_x_orders.add(matched_order.order_id)                # add expected matched_order(X)
            self._orders_by_id.pop(matched_order_node.orders.popleft().order_id)  # del matched_order from dict and tree
            new_order.qty = 0
            if len(matched_order_node.orders) == 0:
                matched_order_node.remove_me()

        # new_order.qty < matched_order.qty
        # 1. decrease matched_order.qty
        # 2. register expected messages: trade, new_order(X)
        # new_order fully filled nothing else to do
        elif new_order.qty < matched_order.qty:
            matched_order.qty = matched_order.qty - new_order.qty
            self._expected_trades.append(Trade(new_order.qty, matched_order.price))  # add expected Trade
            self._expected_x_orders.add(new_order.order_id)                     # add expected new_order(X)
            new_order.qty = 0

        # new_order.qty > matched_order.qty
        # 1. decrease new_order.qty
        # 2. register expected messages: trade, matched_order(X)
        # 3. remove matched_order from the book
        # 4. remove the node from the tree if no more orders with the same price
        #    otherwise recursive call to try to fill the rest of qty
        else:
            new_order.qty = new_order.qty - matched_order.qty
            self._expected_trades.append(Trade(matched_order.qty, matched_order.price))
            self._expected_x_orders.add(matched_order.order_id)                    # add expected matched_order(X)
            self._orders_by_id.pop(matched_order_node.orders.popleft().order_id)  # del matched_order from dict and tree
            if len(matched_order_node.orders) == 0:
                matched_order_node.remove_me()
            else:
                self._process_matched_orders(new_order, matched_order_node)

    def _process_add_sell_order(self, s_order: Order):
        # get best buy orders (max price)
        b_order_node = self._b_orders_by_price.find_rightmost_node()

        # sell price > than best buy price (no match)
        # add sell order to the book
        if s_order.price > b_order_node.price:
            self._s_orders_by_price.insert(s_order.price, s_order)
            self._orders_by_id[s_order.order_id] = s_order

        # sell price <= than best buy price (yes match)
        # try to fulfill
        else:
            self._process_matched_orders(s_order, b_order_node)
            if s_order.qty > 0:
                # try to fulfill again : recursive call
                self._process_add_sell_order(s_order)

    def _process_add_buy_order(self, b_order: Order):
        # get best sell orders (min price)
        s_order_node = self._s_orders_by_price.find_leftmost_node()

        # buy price < than best sell price (no match)
        # add buy order to the book
        if b_order.price < s_order_node.price:
            self._b_orders_by_price.insert(b_order.price, b_order)
            self._orders_by_id[b_order.order_id] = b_order

        # buy price >= best sell price (yes match)
        # try to fulfill
        else:
            self._process_matched_orders(b_order, s_order_node)
            if b_order.qty > 0:
                # try to fill again : recursive call
                self._process_add_buy_order(b_order)

    # !!! removing an order from the tree by price and order_id can be expensive !!!
    # assumption is that these types of removes are rare and there are few orders with same price
    # more ofter removes occur as result of trades (handled in process_matched_orders)
    def _remove_order_from_tree(self, order):
        tree = self._s_orders_by_price if order.side == SideEnum.S else self._b_orders_by_price
        existing_node = tree.find(order.price)
        existing_node.orders.remove(order)
        if len(existing_node.orders) == 0:
            existing_node.remove_me()

    def _update_latest_price_trade_history(self, trade: Trade):
        if self._recent_trade_price == trade.price:
            self._recent_trade_qty += trade.qty
        else:
            self._recent_trade_price = trade.price
            self._recent_trade_qty = trade.qty

    def _report_any_expected_trades_as_missing(self):
        # pop trades from expected_trades deque and report
        while len(self._expected_trades) > 0:
            expected_trade = self._expected_trades.popleft()
            self._update_latest_price_trade_history(expected_trade)
            self._errors.add(ErrorEnum.MissingTrade, expected_trade.to_string())

    def process_trade(self, trade: Trade):
        # pop trades from expected_trades deque till match is found
        while len(self._expected_trades) > 0:
            expected_trade = self._expected_trades.popleft()
            self._update_latest_price_trade_history(expected_trade)

            # operator __eq__ is overloaded
            if trade == expected_trade:
                # found expected trade. return without error
                return
            else:
                # trade did not match. re
                self._errors.add(ErrorEnum.MissingTrade, expected_trade.to_string())

        # trade was not found. report a TradeWithNoOrder error
        self._errors.add(ErrorEnum.TradeWithNoOrder, trade.to_string())

    def process_add_order(self, order: Order):

        # order id already exists in dict. report DuplicateOrder error
        if order.order_id in self._orders_by_id:
            self._errors.add(ErrorEnum.DuplicateOrder, str(order.order_id))
            return

        # in case of missing order(X) or out of order messages.
        # remove the order from expected_x_orders
        if order.order_id in self._expected_x_orders:
            self._expected_x_orders.remove(order.order_id)

        # call add_sell or add_buy
        self._process_add_sell_order(order) if order.side == SideEnum.S else self._process_add_buy_order(order)

    def process_modify_order(self, order: Order):
        existing_order = self._orders_by_id.get(order.order_id, None)

        # if order does not exist treat it as an "add"
        # this will help keeping the book updated in case of lost or out of order msg
        if existing_order is None:
            self.process_add_order(order)
        else:
            # if only qty changed then simply change qty
            if existing_order.side == order.side and existing_order.price == order.price:
                existing_order.qty = order.qty

            #  if side or price has changed then remove and re-add the order
            else:
                self._orders_by_id.pop(existing_order.order_id)
                self._remove_order_from_tree(existing_order)
                self.process_add_order(order)

    def process_remove_order(self, order: Order):
        # if order has already been removed as result of expected trade
        if order.order_id in self._expected_x_orders:
            self._expected_x_orders.remove(order.order_id)
            return

        # remove an existing order from dict and tree
        # report an RemoveWithNoOrder error if order does not exist
        existing_order = self._orders_by_id.pop(order.order_id, None)
        if existing_order is not None:
            self._remove_order_from_tree(existing_order)
        else:
            self._errors.add(ErrorEnum.RemoveWithNoOrder, str(order.order_id))

    def process_message(self, values: List):
        if len(values) == 0:
            # empty line. ignore
            return None
        action_str = values.pop(0)
        try:
            action = ActionEnum[action_str]
            # Trade
            if action == ActionEnum.T:
                self.process_trade(Trade.parse(values))
            # Order
            else:
                self._report_any_expected_trades_as_missing()
                order = Order.from_list(values)
                if action == ActionEnum.A:
                    self.process_add_order(order)
                elif action == ActionEnum.M:
                    self.process_modify_order(order)
                else:  # action == ActionEnum.X:
                    self.process_remove_order(order)
            return action
        except KeyError:
            self._errors.add(ErrorEnum.CorruptedMessage, self._format_error(action_str, values, "Invalid Action"))
        except CorruptedMessageError as er:
            self._errors.add(ErrorEnum.CorruptedMessage, self._format_error(action_str, values, er))
        except InvalidValueError as er:
            self._errors.add(ErrorEnum.InvalidValue, self._format_error(action_str, values, er))
        return None

    def print_errors(self):
        self._errors.print()

    @staticmethod
    def _format_error(action, body, error):
        return str.format("Action:[{}] Body{} Error[{}]", action, body, error)

    @staticmethod
    def _print_node(side, node: Tree):
        quantities = ",".join(side + str(order.qty) for order in node.orders)
        print(node.price, quantities)

    def print_book(self):
        print("Book")

        # sell's root is artificial MAX - skip to the left
        if self._s_orders_by_price.left is not None:
            self._s_orders_by_price.left.travers_reverse(lambda node: self._print_node("S", node))

        # buy's root is artificial MIN - skip to the right
        if self._b_orders_by_price.right is not None:
            self._b_orders_by_price.right.travers_reverse(lambda node: self._print_node("B", node))

    def print_mid_quote(self):
        print(str.format("MidQuote={}", self.calculate_mid_quote()))

    def calculate_mid_quote(self):
        # sell's root is artificial MAX - skip to the left
        # buy's root is artificial MIN - skip to the right

        if self._s_orders_by_price.left is None or self._b_orders_by_price.right is None:
            return "NAN"
        else:
            best_sell_price = self._s_orders_by_price.left.find_leftmost_node().price
            best_buy_price = self._b_orders_by_price.right.find_rightmost_node().price
            return (best_sell_price + best_buy_price) / 2

    def print_recent_price_trades(self):
        print(str.format("RecentPriceTrade={}@{}", self._recent_trade_qty, self._recent_trade_price))

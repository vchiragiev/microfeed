import random
import config
from enums import SideEnum, ActionEnum
from feedhandler import FeedHandler


def generate_order_message(order_id: int):
    min_price = int(config.MIN_PRICE_THRESHOLD)
    max_price = int(config.MAX_PRICE_THRESHOLD)
    price = random.randint(min_price, max_price)
    qty = random.randint(1, 100)
    side = SideEnum(random.randint(int(SideEnum.S.value), int(SideEnum.B.value)))
    action = ActionEnum(random.randint(int(ActionEnum.A.value), int(ActionEnum.A.value)))
    return [action.name, order_id, side.name, qty, price]


if __name__ == "__main__":

    counter = 0
    feed_handler = FeedHandler()
    while counter <= 100000:
        counter += 1
        feed_handler.process_message(generate_order_message(counter))
        feed_handler.print_mid_quote()
        feed_handler.print_recent_price_trades()
    feed_handler.print_book()

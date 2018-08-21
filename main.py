import csv
import argparse
from feedhandler import FeedHandler
import config
from enums import ActionEnum


def process_messages(messages):
    feed_handler = FeedHandler()
    counter: int = 0
    for messageValues in messages:
        counter += 1
        action = feed_handler.process_message(messageValues)
        if counter % 10 == 0:
            feed_handler.print_book()
        feed_handler.print_mid_quote()
        if action == ActionEnum.T:
            feed_handler.print_recent_price_trades()
    feed_handler.print_book()
    feed_handler.print_errors()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process messages')
    parser.add_argument('file_name')
    parser.add_argument('--min_price', required=False, type=float, help="min price threshold",
                        default=config.MIN_PRICE_THRESHOLD)
    parser.add_argument('--max_price', required=False, type=float, help="max price threshold",
                        default=config.MAX_PRICE_THRESHOLD)
    args = parser.parse_args()
    config.MIN_PRICE_THRESHOLD = args.min_price
    config.MAX_PRICE_THRESHOLD = args.max_price

    csv_file = open(args.file_name, "r")
    csv_file_reader = csv.reader(csv_file)
    process_messages(csv_file_reader)


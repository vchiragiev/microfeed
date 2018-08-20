import csv
import argparse
from feedhandler import FeedHandler
import config


def main(file_name):
    csv_file = open(file_name, "r")
    csv_file_reader = csv.reader(csv_file)
    feed_handler = FeedHandler()
    for messageValues in csv_file_reader:
        feed_handler.process_message(messageValues)
    feed_handler.print_errors()
    feed_handler.print_book()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process messages')
    parser.add_argument('file_name')
    parser.add_argument('--min_price', required=False, type=float, help="min price threshold", default=0.0001)
    parser.add_argument('--max_price', required=False, type=float, help="max price threshold", default=1100.0)
    args = parser.parse_args()
    config.MIN_PRICE_THRESHOLD = args.min_price
    config.MAX_PRICE_THRESHOLD = args.max_price
    main(args.file_name)

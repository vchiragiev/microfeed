import csv
import argparse
from feedhandler import FeedHandler
from errorsdict import ErrorsDictionary


def print_messages(messages):
    print(">>> Messages <<<")
    for message in messages:
        print(message.to_string())


def main(file_name):
    ErrorsDictionary.init()
    csv_file = open(file_name, "r")
    csv_file_reader = csv.reader(csv_file )
    feed = FeedHandler()
    for messageValues in csv_file_reader:
        feed.process_message(messageValues)
    print_messages(feed.messages)
    # ErrorsDictionary.print()
    feed.print_book()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process messages')
    parser.add_argument('file_name')
    args = parser.parse_args()
    main(args.file_name)


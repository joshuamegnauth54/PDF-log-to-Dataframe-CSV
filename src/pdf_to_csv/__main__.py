from argparse import ArgumentParser, Namespace

from parser import log_parser
from pathlib import Path


def parse_args() -> Namespace:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("logpath", type=Path, help="path to log to parse")
    parser.add_argument("csvpath", type=Path, help="path to CSV to save")

    return parser.parse_args()


if __name__ == "__main__":
    args: Namespace = parse_args()

    # TODO: Handle logging and log parser
    log_parser(args.logpath)

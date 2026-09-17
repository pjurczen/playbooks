import argparse
import sys

from .report import build_report

MAX_RETRIES = 3


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="reportgen")
    parser.add_argument("names", nargs="+", help="source names under data/")
    parser.add_argument("--fresh", action="store_true", help="bypass both caches")
    parser.add_argument("--retries", type=int, default=MAX_RETRIES, help="retries per source read")
    args = parser.parse_args(argv)
    print(build_report(args.names, fresh=args.fresh))
    return 0


if __name__ == "__main__":
    sys.exit(main())

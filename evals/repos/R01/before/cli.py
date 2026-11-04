import sys

from report import render


def main(argv):
    rows = [("north", 12), ("south", 7)]
    print(render(rows, compact="--compact" in argv))


if __name__ == "__main__":
    main(sys.argv[1:])

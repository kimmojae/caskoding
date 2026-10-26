"""python -m caskoding: fetch upstream fonts and build all twelve Caskoding styles."""

import argparse
from pathlib import Path

from caskoding.build import build
from caskoding.upstream import ensure_upstream
from caskoding.variants import VARIANTS


def main() -> None:
    parser = argparse.ArgumentParser(prog="caskoding")
    parser.add_argument("--out", type=Path, default=Path("fonts"))
    args = parser.parse_args()

    cascadia, d2coding = ensure_upstream()
    for variant in VARIANTS:
        print(build(variant, cascadia, d2coding, args.out))


if __name__ == "__main__":
    main()

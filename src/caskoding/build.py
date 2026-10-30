"""Build one Caskoding font file."""

from pathlib import Path

from fontTools.ttLib import TTFont

from caskoding.merge import FAMILY, merge_d2coding, rename
from caskoding.variants import Variant


def build(variant: Variant, cascadia_dir: Path, d2coding_dir: Path, out_dir: Path) -> Path:
    font = TTFont(cascadia_dir / variant.latin_file)
    merge_d2coding(font, TTFont(d2coding_dir / variant.hangul_file))
    rename(font, variant)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{FAMILY}-{variant.stem}.ttf"
    font.save(path)
    return path

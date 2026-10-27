from pathlib import Path

import pytest
from fontTools.ttLib import TTFont

from caskoding.merge import merge_d2coding, merge_symbols
from caskoding.upstream import ensure_upstream
from caskoding.variants import Variant

REPO = Path(__file__).parent.parent
REGULAR = Variant("Regular", italic=False)


@pytest.fixture(scope="session")
def upstream_dirs() -> tuple[Path, Path, Path]:
    return ensure_upstream(REPO / "upstream")


@pytest.fixture(scope="session")
def merged_regular(upstream_dirs) -> TTFont:
    cascadia, d2coding, juliamono = upstream_dirs
    font = TTFont(cascadia / REGULAR.latin_file)
    merge_symbols(font, TTFont(juliamono / REGULAR.symbols_file))
    merge_d2coding(font, TTFont(d2coding / REGULAR.hangul_file))
    return font

import pytest
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

from caskoding.build import build
from caskoding.variants import VARIANTS

RESERVED = ("Cascadia", "Caskaydia", "D2Coding")


@pytest.fixture(scope="session")
def built_fonts(upstream_dirs, tmp_path_factory) -> dict[str, TTFont]:
    out = tmp_path_factory.mktemp("fonts")
    return {v.stem: TTFont(build(v, *upstream_dirs, out)) for v in VARIANTS}


def _name(font: TTFont, name_id: int) -> str:
    return font["name"].getName(name_id, 3, 1, 0x409).toUnicode()


def test_four_variants_map_to_existing_upstream_files(upstream_dirs):
    cascadia, d2coding, juliamono = upstream_dirs
    assert len(VARIANTS) == 4
    assert all((cascadia / v.latin_file).exists() for v in VARIANTS)
    assert all((d2coding / v.hangul_file).exists() for v in VARIANTS)
    assert all((juliamono / v.symbols_file).exists() for v in VARIANTS)


def test_bold_weights_use_d2coding_bold():
    bold = {v.stem for v in VARIANTS if v.hangul_file.startswith("D2CodingBold")}
    assert bold == {"Bold", "BoldItalic"}


def test_rename_regular(built_fonts):
    font = built_fonts["Regular"]
    assert _name(font, 1) == "Caskoding"
    assert _name(font, 2) == "Regular"
    assert _name(font, 3) == "Caskoding Regular 0.1.0"
    assert _name(font, 4) == "Caskoding Regular"
    assert _name(font, 6) == "Caskoding-Regular"
    assert _name(font, 16) == "Caskoding"


def test_no_reserved_names_left(built_fonts):
    for font in built_fonts.values():
        for record in font["name"].names:
            if record.nameID in (1, 3, 4, 6, 16):
                text = record.toUnicode()
                assert not any(word in text for word in RESERVED), text


def test_variant_names_unique(built_fonts):
    fonts = built_fonts.values()
    assert len({_name(f, 6) for f in fonts}) == 4
    assert len({(_name(f, 16), _name(f, 17) if f["name"].getName(17, 3, 1, 0x409) else _name(f, 2)) for f in fonts}) == 4


def test_bold_hangul_within_line_height(built_fonts):
    font = built_fonts["Bold"]
    cmap, glyphs = font.getBestCmap(), font.getGlyphSet()
    ymin = ymax = 0
    for cp in range(0xAC00, 0xD7A4):
        pen = BoundsPen(glyphs)
        glyphs[cmap[cp]].draw(pen)
        ymin, ymax = min(ymin, pen.bounds[1]), max(ymax, pen.bounds[3])
    assert ymin - (-480) >= 30
    assert 1900 - ymax >= 30


def test_style_bits(built_fonts, upstream_dirs):
    for variant in VARIANTS:
        font = built_fonts[variant.stem]
        original = TTFont(upstream_dirs[0] / variant.latin_file)
        assert font["OS/2"].usWeightClass == original["OS/2"].usWeightClass
        assert font["OS/2"].fsSelection == original["OS/2"].fsSelection
        assert font["head"].macStyle == original["head"].macStyle

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

from caskoding.variants import Variant

REGULAR = Variant("Regular", italic=False)
SYLLABLES = range(0xAC00, 0xD7A4)
COMPAT_JAMO = range(0x3131, 0x318F)


def _ink_bounds(font: TTFont, codepoints) -> list[tuple[float, float, float, float]]:
    cmap, glyphs = font.getBestCmap(), font.getGlyphSet()
    result = []
    for cp in codepoints:
        pen = BoundsPen(glyphs)
        glyphs[cmap[cp]].draw(pen)
        result.append(pen.bounds)
    return result


def test_adds_all_hangul(merged_regular):
    cmap = merged_regular.getBestCmap()
    assert all(cp in cmap for cp in SYLLABLES)
    assert all(cp in cmap for cp in COMPAT_JAMO)


def test_hangul_is_two_cells(merged_regular):
    hmtx, cmap = merged_regular["hmtx"], merged_regular.getBestCmap()
    assert hmtx[cmap[ord("M")]][0] == 1200
    assert {hmtx[cmap[cp]][0] for cp in SYLLABLES} == {2400}


def test_hangul_ink_within_line_height(merged_regular):
    bounds = _ink_bounds(merged_regular, SYLLABLES)
    assert min(b[1] for b in bounds) >= -480
    assert max(b[3] for b in bounds) <= 1900
    assert min(b[0] for b in bounds) >= 0
    assert max(b[2] for b in bounds) <= 2400


def test_hangul_margins_balanced(merged_regular):
    bounds = _ink_bounds(merged_regular, SYLLABLES)
    top_margin = 1900 - max(b[3] for b in bounds)
    bottom_margin = min(b[1] for b in bounds) - (-480)
    assert abs(top_margin - bottom_margin) <= 2


def test_hangul_keeps_d2coding_proportion(merged_regular, upstream_dirs):
    original = TTFont(upstream_dirs[1] / REGULAR.hangul_file)

    def ratio(font):
        (bounds,) = _ink_bounds(font, [0xD55C])  # 한
        return (bounds[3] - bounds[1]) / font["OS/2"].sCapHeight

    assert abs(ratio(merged_regular) / ratio(original) - 1) <= 0.01


def test_hangul_centred_in_cell(merged_regular):
    bounds = _ink_bounds(merged_regular, SYLLABLES)
    left = min(b[0] for b in bounds)
    right = 2400 - max(b[2] for b in bounds)
    assert abs(left - right) <= 2


def test_existing_glyphs_untouched(merged_regular, upstream_dirs):
    original = TTFont(upstream_dirs[0] / REGULAR.latin_file)
    orig_cmap, new_cmap = original.getBestCmap(), merged_regular.getBestCmap()
    assert all(new_cmap[cp] == name for cp, name in orig_cmap.items())

    for cp in (ord("A"), ord("0"), 0xE0A0):
        name = orig_cmap[cp]
        before, after = RecordingPen(), RecordingPen()
        original.getGlyphSet()[name].draw(before)
        merged_regular.getGlyphSet()[name].draw(after)
        assert after.value == before.value
        assert merged_regular["hmtx"][name] == original["hmtx"][name]


def test_merged_font_saves_and_reloads(merged_regular, tmp_path):
    path = tmp_path / "merged.ttf"
    merged_regular.save(path)

    reloaded = TTFont(path)
    assert 0xAC00 in reloaded.getBestCmap()
    assert reloaded["maxp"].numGlyphs == len(reloaded.getGlyphOrder())

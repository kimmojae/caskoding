from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

from caskoding.merge import merge_d2coding, merge_symbols
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


def test_fills_terminal_ui_symbols_at_one_cell(merged_regular):
    hmtx, cmap = merged_regular["hmtx"], merged_regular.getBestCmap()
    for ch in "⎿⏺⏵⏸⏴⧉✻✳✶✢✽↯⚠✔✗✘①※○":
        assert hmtx[cmap[ord(ch)]][0] == 1200, ch


def test_symbols_keep_baseline_and_proportion(merged_regular, upstream_dirs):
    original = TTFont(upstream_dirs[2] / REGULAR.symbols_file)

    def bounds(font):
        (b,) = _ink_bounds(font, [ord("✔")])
        return [v / font["OS/2"].sCapHeight for v in b]

    merged_b, original_b = bounds(merged_regular), bounds(original)
    assert abs(merged_b[1] - original_b[1]) <= 0.01  # bottom: same baseline offset
    assert abs((merged_b[3] - merged_b[1]) - (original_b[3] - original_b[1])) <= 0.01


def test_symbols_take_precedence_over_d2coding(upstream_dirs):
    cascadia, d2coding, juliamono = upstream_dirs
    font = TTFont(cascadia / REGULAR.latin_file)
    merge_symbols(font, TTFont(juliamono / REGULAR.symbols_file))
    name = font.getBestCmap()[ord("✔")]
    before = RecordingPen()
    font.getGlyphSet()[name].draw(before)

    merge_d2coding(font, TTFont(d2coding / REGULAR.hangul_file))
    after = RecordingPen()
    font.getGlyphSet()[font.getBestCmap()[ord("✔")]].draw(after)
    assert after.value == before.value


def test_symbols_outside_bmp_only_in_full_cmap(merged_regular):
    cp = 0x1D400  # MATHEMATICAL BOLD CAPITAL A
    for table in merged_regular["cmap"].tables:
        if table.isUnicode() and table.format != 14:
            assert (cp in table.cmap) == (table.format == 12)


def test_fills_wide_cjk_at_two_cells(merged_regular):
    hmtx, cmap = merged_regular["hmtx"], merged_regular.getBestCmap()
    for ch in "漢字「」、":
        assert hmtx[cmap[ord(ch)]][0] == 2400, ch


def test_skips_width_mismatch_and_private_use(merged_regular, upstream_dirs):
    original = TTFont(upstream_dirs[1] / REGULAR.hangul_file)
    cmap, latin = merged_regular.getBestCmap(), TTFont(upstream_dirs[0] / REGULAR.latin_file)
    # D2Coding draws ① two cells wide, but terminals give it one, so it never comes
    # from D2Coding; JuliaMono supplies it at one cell instead.
    assert 0x2460 in original.getBestCmap()
    assert merged_regular["hmtx"][cmap[0x2460]][0] == 1200
    d2_private = [cp for cp in original.getBestCmap() if 0xE000 <= cp <= 0xF8FF]
    latin_cmap = latin.getBestCmap()
    assert all(cmap.get(cp) == latin_cmap.get(cp) for cp in d2_private)


def test_d2coding_fallback_ink_within_cell(merged_regular, upstream_dirs):
    # JuliaMono glyphs are copied as designed (stacked accents may rise above the
    # line), so only check what D2Coding supplied.
    cascadia, _, juliamono = upstream_dirs
    skip = set(TTFont(cascadia / REGULAR.latin_file).getBestCmap())
    skip |= set(TTFont(juliamono / REGULAR.symbols_file).getBestCmap())
    cmap, hmtx = merged_regular.getBestCmap(), merged_regular["hmtx"]
    added = [cp for cp in cmap if cp not in skip and not 0xAC00 <= cp <= 0xD7A3]
    for cp, bounds in zip(added, _ink_bounds(merged_regular, added)):
        if bounds is None:
            continue
        assert bounds[1] >= -480 and bounds[3] <= 1900, hex(cp)
        assert bounds[0] >= -1 and bounds[2] <= hmtx[cmap[cp]][0] + 1, hex(cp)


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

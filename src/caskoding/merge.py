"""Fill a CaskaydiaMono font's gaps from JuliaMono (symbols) and D2Coding (Hangul, CJK) at terminal width."""

import unicodedata

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from caskoding.variants import Variant

HANGUL_RANGES: tuple[tuple[int, int], ...] = ((0x3131, 0x318E), (0xAC00, 0xD7A3))
# Zero-width marks, controls, and private use (Nerd Font icons live there) are never filled.
SKIPPED_CATEGORIES = frozenset({"Mn", "Me", "Cc", "Cf", "Co", "Cs", "Zl", "Zp"})

FAMILY = "Caskoding"
VERSION = "0.1.0"
# Longest first, so "CaskaydiaMono NFM" does not eat the start of the full name.
UPSTREAM_FAMILY_NAMES = ("CaskaydiaMono Nerd Font Mono", "CaskaydiaMono NFM", "CaskaydiaMonoNFM")

OS2_RANGE_FIELDS = (
    "ulUnicodeRange1",
    "ulUnicodeRange2",
    "ulUnicodeRange3",
    "ulUnicodeRange4",
    "ulCodePageRange1",
    "ulCodePageRange2",
)


def _terminal_cells(cp: int) -> int:
    """How many cells a terminal gives `cp`: two for East Asian Wide/Fullwidth, else one."""
    return 2 if unicodedata.east_asian_width(chr(cp)) in "WF" else 1


def _fillable(cp: int, latin_cmap: dict) -> bool:
    return cp not in latin_cmap and unicodedata.category(chr(cp)) not in SKIPPED_CATEGORIES


def merge_symbols(latin: TTFont, symbols: TTFont) -> int:
    """Fill Cascadia's one-cell gaps from JuliaMono in place; return how many were added.

    Two-cell codepoints are left for D2Coding, whose Hangul and Hanja they sit beside.
    """
    latin_cmap, symbols_cmap = latin.getBestCmap(), symbols.getBestCmap()
    codepoints = [
        cp for cp in sorted(symbols_cmap) if _fillable(cp, latin_cmap) and _terminal_cells(cp) == 1
    ]
    added = _copy_centred(latin, symbols, codepoints)
    _register(latin, added)
    return len(added)


def merge_d2coding(latin: TTFont, d2coding: TTFont) -> int:
    """Fill glyphs still missing from D2Coding in place; return how many were added.

    Hangul is fitted as a block into two cells. Every other D2Coding glyph follows
    if its D2Coding width matches the terminal's: D2Coding draws ambiguous-width
    characters (①, ※, ○, …) two cells wide while terminals give them one, so
    those would overlap their neighbour.
    """
    latin_cmap, d2_cmap = latin.getBestCmap(), d2coding.getBestCmap()
    d2_glyphs, d2_hmtx = d2coding.getGlyphSet(), d2coding["hmtx"]
    d2_upm = d2coding["head"].unitsPerEm
    hangul = {cp for lo, hi in HANGUL_RANGES for cp in range(lo, hi + 1)}
    hangul_codepoints = [cp for cp in sorted(hangul) if cp in d2_cmap and cp not in latin_cmap]
    other_codepoints = [
        cp
        for cp in sorted(d2_cmap)
        if cp not in hangul
        and _fillable(cp, latin_cmap)
        and d2_hmtx[d2_cmap[cp]][0] * 2 == _terminal_cells(cp) * d2_upm
    ]

    scale = _scale(latin, d2coding)
    wide = 2 * _cell(latin)

    # Centre the whole Hangul ink range in the cell so opposite margins match.
    # A BoundsPen accumulates, so drawing every glyph into one gives their union.
    pen = BoundsPen(d2_glyphs)
    for cp in hangul_codepoints:
        d2_glyphs[d2_cmap[cp]].draw(pen)
    xmin, ymin, xmax, ymax = pen.bounds
    hhea = latin["hhea"]
    dx = wide / 2 - scale * (xmin + xmax) / 2
    dy = (hhea.ascent + hhea.descent) / 2 - scale * (ymin + ymax) / 2

    added = {
        cp: _copy_glyph(latin, d2_glyphs, d2_cmap[cp], cp, scale, dx, dy, wide)
        for cp in hangul_codepoints
    }
    # Wide glyphs (Hanja, CJK punctuation) share Hangul's vertical shift.
    added |= _copy_centred(latin, d2coding, other_codepoints, wide_dy=dy)
    _register(latin, added)

    latin_os2, d2_os2 = latin["OS/2"], d2coding["OS/2"]
    for field in OS2_RANGE_FIELDS:
        setattr(latin_os2, field, getattr(latin_os2, field) | getattr(d2_os2, field))
    hhea.advanceWidthMax = max(hhea.advanceWidthMax, wide)
    return len(added)


def _cell(latin: TTFont) -> int:
    return latin["hmtx"][latin.getBestCmap()[ord("M")]][0]


def _scale(latin: TTFont, source: TTFont) -> float:
    # Sized by cap height so the source keeps its proportion to Latin. Scaling
    # D2Coding's em to fill the (wider) Cascadia cells would make it about 17% too big.
    return latin["OS/2"].sCapHeight / source["OS/2"].sCapHeight


def _copy_centred(
    latin: TTFont, source: TTFont, codepoints: list[int], wide_dy: float = 0.0
) -> dict[int, str]:
    """Copy monospaced glyphs into their terminal cells, centred by advance.

    One-cell glyphs keep the source baseline, which the cap-height scale already
    lines up with Cascadia's; two-cell glyphs are shifted by `wide_dy`.
    """
    source_cmap, source_glyphs, source_hmtx = source.getBestCmap(), source.getGlyphSet(), source["hmtx"]
    scale, cell = _scale(latin, source), _cell(latin)
    added = {}
    for cp in codepoints:
        name = source_cmap[cp]
        cells = _terminal_cells(cp)
        advance = cells * cell
        dx = (advance - scale * source_hmtx[name][0]) / 2
        dy = wide_dy if cells == 2 else 0.0
        added[cp] = _copy_glyph(latin, source_glyphs, name, cp, scale, dx, dy, advance)
    return added


def _copy_glyph(
    latin: TTFont, glyphs, source_name: str, cp: int, scale: float, dx: float, dy: float, advance: int
) -> str:
    """Redraw one source glyph into `latin` as uniXXXX (or uXXXXX), scaled then shifted."""
    glyf = latin["glyf"]
    name = f"uni{cp:04X}" if cp <= 0xFFFF else f"u{cp:05X}"
    recording = DecomposingRecordingPen(glyphs)
    glyphs[source_name].draw(recording)
    pen = TTGlyphPen(None)
    recording.replay(TransformPen(pen, (scale, 0, 0, scale, dx, dy)))
    glyph = pen.glyph()
    glyph.recalcBounds(glyf)
    glyf[name] = glyph  # also appends name to glyf.glyphOrder
    latin["hmtx"][name] = (advance, getattr(glyph, "xMin", 0))
    return name


def _register(latin: TTFont, added: dict[int, str]) -> None:
    """Sync the glyph order and map `added` in every Unicode cmap that can hold it."""
    latin.setGlyphOrder(latin["glyf"].glyphOrder)
    bmp = {cp: name for cp, name in added.items() if cp <= 0xFFFF}
    for table in latin["cmap"].tables:
        if table.isUnicode() and table.format != 14:
            table.cmap.update(added if table.format == 12 else bmp)


def rename(font: TTFont, variant: Variant) -> None:
    """Rename the CaskaydiaMono name records to Caskoding for one variant."""
    name_table = font["name"]
    kept, seen = [], set()
    for record in name_table.names:
        key = (record.platformID, record.platEncID, record.langID, record.nameID)
        if record.nameID == 7 or key in seen:  # drop Cascadia trademark and duplicates
            continue
        seen.add(key)
        text = record.toUnicode()
        if record.nameID == 0:
            text += (
                "\nHangul and fallback glyphs © 2015 NAVER Corporation (D2Coding)."
                "\nSymbol glyphs © 2020-2023 cormullion (JuliaMono)."
            )
        elif record.nameID == 3:
            text = f"{FAMILY} {variant.style} {VERSION}"
        elif record.nameID == 5:
            text += f"; {FAMILY} {VERSION}"
        else:
            for upstream in UPSTREAM_FAMILY_NAMES:
                text = text.replace(upstream, FAMILY)
        record.string = text
        kept.append(record)
    name_table.names = kept

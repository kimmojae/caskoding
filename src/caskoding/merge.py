"""Copy D2Coding Hangul into a CaskaydiaMono font at exactly two cells wide."""

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from caskoding.variants import Variant

HANGUL_RANGES: tuple[tuple[int, int], ...] = ((0x3131, 0x318E), (0xAC00, 0xD7A3))

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


def merge_hangul(latin: TTFont, hangul: TTFont) -> int:
    """Add Hangul glyphs from `hangul` to `latin` in place; return how many were added."""
    latin_cmap, hangul_cmap = latin.getBestCmap(), hangul.getBestCmap()
    hangul_glyphs = hangul.getGlyphSet()
    codepoints = [
        cp
        for lo, hi in HANGUL_RANGES
        for cp in range(lo, hi + 1)
        if cp in hangul_cmap and cp not in latin_cmap
    ]

    # Two Latin cells wide, but sized by cap height so Hangul keeps D2Coding's
    # proportion to Latin. Scaling the Hangul em to fill two (wider) Cascadia
    # cells would make it about 17% too big.
    wide = 2 * latin["hmtx"][latin_cmap[ord("M")]][0]
    scale = latin["OS/2"].sCapHeight / hangul["OS/2"].sCapHeight

    # Centre the whole Hangul ink range in the cell so opposite margins match.
    # A BoundsPen accumulates, so drawing every glyph into one gives their union.
    pen = BoundsPen(hangul_glyphs)
    for cp in codepoints:
        hangul_glyphs[hangul_cmap[cp]].draw(pen)
    xmin, ymin, xmax, ymax = pen.bounds
    hhea = latin["hhea"]
    dx = wide / 2 - scale * (xmin + xmax) / 2
    dy = (hhea.ascent + hhea.descent) / 2 - scale * (ymin + ymax) / 2

    glyf, hmtx = latin["glyf"], latin["hmtx"]
    added = {}
    for cp in codepoints:
        name = f"uni{cp:04X}"
        recording = DecomposingRecordingPen(hangul_glyphs)
        hangul_glyphs[hangul_cmap[cp]].draw(recording)
        pen = TTGlyphPen(None)
        recording.replay(TransformPen(pen, (scale, 0, 0, scale, dx, dy)))
        glyph = pen.glyph()
        glyph.recalcBounds(glyf)
        glyf[name] = glyph  # also appends name to glyf.glyphOrder
        hmtx[name] = (wide, getattr(glyph, "xMin", 0))
        added[cp] = name

    latin.setGlyphOrder(glyf.glyphOrder)
    for table in latin["cmap"].tables:
        if table.isUnicode() and table.format != 14:
            table.cmap.update(added)

    latin_os2, hangul_os2 = latin["OS/2"], hangul["OS/2"]
    for field in OS2_RANGE_FIELDS:
        setattr(latin_os2, field, getattr(latin_os2, field) | getattr(hangul_os2, field))
    hhea.advanceWidthMax = max(hhea.advanceWidthMax, wide)
    return len(added)


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
            text += "\nHangul glyphs © 2015 NAVER Corporation (D2Coding)."
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

"""The four Caskoding styles and the upstream files each is built from."""

from dataclasses import dataclass

# Terminals and editors only use these four. D2Coding has just Regular and Bold,
# so lighter or in-between weights would pair thin Latin with Regular Hangul.
WEIGHTS = ("Regular", "Bold")


@dataclass(frozen=True)
class Variant:
    weight: str
    italic: bool

    @property
    def stem(self) -> str:
        if not self.italic:
            return self.weight
        return "Italic" if self.weight == "Regular" else f"{self.weight}Italic"

    @property
    def style(self) -> str:
        if not self.italic:
            return self.weight
        return "Italic" if self.weight == "Regular" else f"{self.weight} Italic"

    @property
    def latin_file(self) -> str:
        return f"CaskaydiaMonoNerdFontMono-{self.stem}.ttf"

    @property
    def hangul_file(self) -> str:
        if self.weight == "Bold":
            return "D2CodingBold-Ver1.4.0-20261003.ttf"
        return "D2Coding-Ver1.4.0-20261003.ttf"


VARIANTS: tuple[Variant, ...] = tuple(
    Variant(weight, italic) for weight in WEIGHTS for italic in (False, True)
)

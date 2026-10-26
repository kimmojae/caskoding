"""The twelve Caskoding styles and the upstream files each is built from."""

from dataclasses import dataclass

WEIGHTS = ("ExtraLight", "Light", "SemiLight", "Regular", "SemiBold", "Bold")
BOLD_HANGUL_WEIGHTS = ("SemiBold", "Bold")


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
        if self.weight in BOLD_HANGUL_WEIGHTS:
            return "D2CodingBold-Ver1.4.0-20261003.ttf"
        return "D2Coding-Ver1.4.0-20261003.ttf"


VARIANTS: tuple[Variant, ...] = tuple(
    Variant(weight, italic) for weight in WEIGHTS for italic in (False, True)
)

.PHONY: fonts test install uninstall clean

FONT_DIR := $(HOME)/Library/Fonts

fonts:
	uv run python -m caskoding

test:
	uv run pytest

install: fonts
	cp fonts/Caskoding-*.ttf $(FONT_DIR)/

uninstall:
	rm -f $(FONT_DIR)/Caskoding-*.ttf

clean:
	rm -rf fonts

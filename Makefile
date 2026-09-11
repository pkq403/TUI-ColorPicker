.PHONY: install uninstall test

install:
	@bash install.sh install

uninstall:
	@bash install.sh --uninstall

test:
	uv run pytest

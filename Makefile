.PHONY: build install clean shell

dev:
	uv run python -m podtool.main

build: # produces ./result/bin/podtool
	nix build .

run: build
	./result/bin/podtool

install: build
	nix profile remove podtool
	nix profile install .

clean:
	rm -rf result

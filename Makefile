.PHONY: build install clean shell

build: # produces ./result/bin/podtool
	nix build .

run: build
	./result/bin/podtool

install: build
	nix profile remove podtool
	nix profile install .

clean:
	rm -rf result

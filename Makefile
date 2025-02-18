.PHONY: build install clean shell

# Build the podtool flake package, which produces a symlink such as ./result
build:
	@echo "Building the podtool flake package..."
	nix build .

# Install the podtool package to your Nix user profile using nix profile (Nix 2.4+)
install: build
	nix profile remove podtool
	nix profile install .

# Optional clean target
clean:
	rm -rf result

# Enter a development shell with all dependencies
shell:
	@echo "Entering development shell..."
	nix develop .
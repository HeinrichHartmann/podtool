.PHONY: build install clean

# Build the podtool flake package, which produces a symlink such as ./result
build:
	@echo "Building the podtool flake package..."
	nix build .

# Install the podtool package to your Nix user profile using nix profile (Nix 2.4+)
install: build
	@echo "Installing podtool from flake..."
	nix profile install .

# Optional clean target
clean:
	@echo "No cleanup is necessary in this setup."
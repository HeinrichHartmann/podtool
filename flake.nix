{
  description = "A podtool CLI tool with ffmpeg and sox dependencies";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        packages.default = pkgs.python3Packages.buildPythonApplication {
          pname = "podtool";
          version = "1.0.0";
          src = ./.;
          format = "pyproject";

          propagatedBuildInputs = with pkgs.python3Packages; [
            setuptools
            click
          ];

          nativeBuildInputs = with pkgs; [
            ffmpeg
            sox
          ];
        };

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
            python3Packages.click
            ffmpeg
            sox
          ];
        };
      }
    );
}

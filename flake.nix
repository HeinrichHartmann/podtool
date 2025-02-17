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
        inputs = (with pkgs.python3Packages; [
            setuptools
            click
          ]) ++ (with pkgs; [
            ffmpeg
            sox
            audacity
          ]);
      in
      {
        packages.default = pkgs.python3Packages.buildPythonApplication {
          pname = "podtool";
          version = "1.0.0";
          src = ./.;
          format = "pyproject";
          propagatedBuildInputs = inputs;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = inputs;
        };
      }
    );
}

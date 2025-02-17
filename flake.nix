{
  description = "A podtool CLI tool with ffmpeg and sox dependencies";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in {
        packages.podtool = pkgs.stdenv.mkDerivation {
          name = "podtool-${self.version or "1.0.0"}";
          version = "1.0.0";
          src = ./.;
          dontBuild = true;
          installPhase = ''
            mkdir -p $out/bin
            cp podtool.sh $out/bin/podtool
            chmod +x $out/bin/podtool

            # Replace the placeholder values in the script
            substituteInPlace $out/bin/podtool \
              --replace 'CMD_FFMPEG' '${pkgs.ffmpeg}/bin/ffmpeg' \
              --replace 'CMD_SOX' '${pkgs.sox}/bin/sox'
          '';
        };

        defaultPackage = self.packages.${system}.podtool;
      });
}

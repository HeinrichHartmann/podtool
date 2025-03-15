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
        # Define non-Python dependencies
        systemDeps = with pkgs; [
          ffmpeg
          sox
          audacity
          python3Packages.uv  # Add uv package
        ];
      in
      {
        packages.default = pkgs.python3Packages.buildPythonApplication {
          pname = "podtool";
          version = "1.0.0";
          src = ./.;
          format = "pyproject";
          
          # Handle dependencies with uv. Nix just provides a build sandbox, and packages the output.
          nativeBuildInputs = [ pkgs.python3Packages.uv ];
          dontCheckRuntimeDeps = true;
          buildPhase = ''
            export UV_CACHE_DIR=$TMPDIR/.cache/uv
            mkdir -p $UV_CACHE_DIR
            uv sync --locked
            uv build --sdist --wheel --out-dir dist
          '';
          installPhase = ''
            runHook preInstall
            
            export UV_CACHE_DIR=$TMPDIR/.cache/uv
            mkdir -p $out/lib/python${pkgs.python3.pythonVersion}/site-packages
            PYTHONPATH=$out/lib/python${pkgs.python3.pythonVersion}/site-packages:$PYTHONPATH
            
            # Install the wheel we just built
            uv pip install dist/*.whl --prefix=$out
            
            # Clean up unwanted binaries, keeping only podtool
            find $out/bin -type f -not -name 'podtool' -delete
            
            runHook postInstall
          '';
          propagatedBuildInputs = systemDeps;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = systemDeps;
          shellHook = ''
            export GOOGLE_APPLICATION_CREDENTIALS="${toString ./service-account.json}"
          '';
        };
      }
    );
}

{
  description = "opendata.fit services flake";

  # Use the unstable nixpkgs to use the latest set of node packages
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/master";

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem
    (system: let
      pkgs = import nixpkgs {
        inherit system;
      };
      pkgsUnstable = import <nixpkgs-unstable> {
        inherit system;
      };
    in {
      devShells.default = pkgs.mkShell {
        buildInputs = [
          pkgs.python310
        ];

        shellHook = ''
          VENV=.venv
          if test ! -d $VENV; then
            python -m venv .venv
          fi
          source ./$VENV/bin/activate
        ''
      };
    });
}

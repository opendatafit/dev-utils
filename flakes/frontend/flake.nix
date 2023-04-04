{
  description = "opendata.fit development environment for the webapp and frontend packages";

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
        defaultPackage.x86_64-linux = self.packages.x86_64-linux.frontend;
      };
    in {
      devShells.default = pkgs.mkShell {
        buildInputs = [
          # Set the major version of Node.js
          pkgs.nodejs-16_x

          pkgs.yarn

          pkgs.nodePackages.typescript
          # pkgs.nodePackages.typescript-language-server
        ];
      };
    });
}

{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
  };

  outputs = { self, nixpkgs }:
  let pkgs = import nixpkgs { system = "x86_64-linux"; };
  in {
    devShell.x86_64-linux = pkgs.mkShell {
      buildInputs = with pkgs; [
        python3
        python311Packages.requests
      ];
    };
  };
}

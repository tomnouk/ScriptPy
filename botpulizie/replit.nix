{ pkgs }: {
  deps = [
    pkgs.mysql-client
    pkgs.systemd
    pkgs.sqlite.bin
  ];
}
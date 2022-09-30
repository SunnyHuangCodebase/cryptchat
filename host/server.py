from __future__ import annotations
from pathlib import Path
import socket
import threading
from typing import TypedDict

try:
  import tomllib    #type: ignore
except ModuleNotFoundError:
  import tomli as tomllib    #type: ignore


class ServerConfig(TypedDict):
  header_size: int
  port: int
  format: str
  disconnect_command: str


class Server:
  """Chat server"""
  header_size: int
  host: str
  port: int
  format: str
  disconnect_command: str
  server: socket.socket

  def __init__(self, config_path: Path):
    config = self.load_config(config_path)

    for item in ServerConfig.__annotations__:
      self.__dict__[item] = config[item]    #type: ignore

    self.host = socket.gethostbyname(socket.gethostname())

  def start(self):
    """Start the server."""
    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server.bind(self.address)
    self.server.listen()
    print(f"[SERVER STARTED] {self.host}")
    while True:
      connection = self.server.accept()    # tuple[socket, address]

      thread = threading.Thread(target=self.listen_on_client, args=connection)
      thread.start()
      print(f"[ACTIVE CONNECTIONS]:{threading.active_count() - 1}")

  def listen_on_client(self, connection: socket.socket, address: tuple[str,
                                                                       int]):
    """Listen for client messages"""
    print(f"[NEW CONNECTION]: {address}")

    while True:
      byte_size = connection.recv(self.header_size).decode(self.format)
      if not byte_size:
        return

      bytes = int(byte_size)
      message = connection.recv(bytes).decode(self.format)
      print(f"[{address}] {message}")
      if message == self.disconnect_command:
        break

      connection.send("Message received".encode(self.format))

    connection.close()

  @property
  def address(self) -> tuple[str, int]:
    return self.host, self.port

  def load_config(self, path: Path) -> ServerConfig:
    with open(path, "rb") as file:
      return tomllib.load(file)    #type: ignore


if __name__ == "__main__":
  config_path = Path(__file__).parent / "server_config.toml"
  server = Server(config_path)
  server.start()

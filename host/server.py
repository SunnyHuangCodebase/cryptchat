from __future__ import annotations
from pathlib import Path
import socket
import threading

try:
  import tomllib    #type: ignore
except ModuleNotFoundError:
  import tomli as tomllib    #type: ignore

from config.config import ServerConfig


class Server:
  """Chat server"""
  header_size: int
  host: str
  port: int
  format: str
  connect_command: str
  disconnect_command: str

  def __init__(self, config_path: Path):
    self.load_config(config_path)

  @property
  def address(self) -> tuple[str, int]:
    return self.host, self.port

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


  def load_config(self, path: Path):
    with open(path, "rb") as file:
      config = tomllib.load(file)    #type: ignore
      for item in ServerConfig.__annotations__:
        self.__dict__[item] = config[item]    #type: ignore


if __name__ == "__main__":
  config_path = Path(__file__).parent / "server_config.toml"
  server = Server(config_path)
  server.start()

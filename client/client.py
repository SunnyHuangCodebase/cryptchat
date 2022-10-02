import json
from pathlib import Path
import socket
from typing import Any

try:
  import tomllib    #type: ignore
except ModuleNotFoundError:
  import tomli as tomllib    #type: ignore

from config.config import ServerConfig


class Client:
  """Chat client"""
  header_size: int
  host: str
  port: int
  format: str
  connect_command: str
  disconnect_command: str

  def __init__(self, config_path: Path):
    self.load_config(config_path)

  @property
  def server_address(self) -> tuple[str, int]:
    return self.host, self.port

  def connect(self):
    """Connect to server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect(self.server_address)
    self.send_message(server, self.connect_command)

    while True:
      print(self.receive_response(server))

      message = input()

      if not message:
        continue

      self.send_message(server, message)

      if message == self.disconnect_command:
        break

  def _send_header(self, server: socket.socket, message: Any):
    """Send message header."""
    header = f"{len(message):<{self.header_size}}"
    server.send(header.encode(self.format))

  def send_message(self, server: socket.socket, message: Any):
    """Send message."""
    json_message = json.dumps(message)
    bytes_message = json_message.encode(self.format)
    self._send_header(server, bytes_message)
    server.send(bytes_message)

  def receive_response(self, server: socket.socket) -> str:
    header = server.recv(self.header_size).decode(self.format)
    buffer_size = int(header)
    response = server.recv(buffer_size)
    response = json.loads(response.decode(self.format))
    return str(response)

  def load_config(self, path: Path):
    with open(path, "rb") as file:
      config = tomllib.load(file)    #type: ignore

      for item in ServerConfig.__annotations__:
        self.__dict__[item] = config[item]    #type: ignore


if __name__ == "__main__":
  config_path = Path(__file__).parent / "client_config.toml"
  client = Client(config_path)
  client.connect()

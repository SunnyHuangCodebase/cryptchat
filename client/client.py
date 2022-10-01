from pathlib import Path
import socket

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
      message = input()

      if not message:
        continue

      self.send_message(server, message)

      if message == self.disconnect_command:
        break

  def _send_header(self, server: socket.socket, message: str):
    """Send message header."""
    header = f"{len(message):<{self.header_size}}"
    server.send(header.encode(self.format))

  def send_message(self, server: socket.socket, message: str):
    """Send message."""
    self._send_header(server, message)
    encoded_message = message.encode(self.format)
    server.send(encoded_message)
    print(self._receive_response(server))

  def _receive_response(self, server: socket.socket) -> str:
    header = server.recv(self.header_size).decode(self.format)

    buffer_size = int(header)
    return server.recv(buffer_size).decode(self.format)

  def load_config(self, path: Path):
    with open(path, "rb") as file:
      config = tomllib.load(file)    #type: ignore

      for item in ServerConfig.__annotations__:
        self.__dict__[item] = config[item]    #type: ignore


if __name__ == "__main__":
  config_path = Path(__file__).parent / "client_config.toml"
  client = Client(config_path)
  client.connect()

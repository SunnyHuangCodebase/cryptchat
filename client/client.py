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
    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.client.connect(self.server_address)
    while True:
      message = input()

      self.send(message)
      if message == self.disconnect_command:
        break

  def send_header(self, message: str):
    """Send message header"""
    message_length = len(message)
    header = f"{message_length:<{self.header_size}}"
    encoded_header = header.encode(self.format)
    self.client.send(encoded_header)

  def send(self, message: str):
    """Send message."""
    self.send_header(message)
    encoded_message = message.encode(self.format)
    self.client.send(encoded_message)
    print(self.client.recv(2048).decode(self.format))

  def load_config(self, path: Path):
    with open(path, "rb") as file:
      config = tomllib.load(file)    #type: ignore

      for item in ServerConfig.__annotations__:
        self.__dict__[item] = config[item]    #type: ignore


if __name__ == "__main__":
  config_path = Path(__file__).parent / "client_config.toml"
  client = Client(config_path)
  client.connect()

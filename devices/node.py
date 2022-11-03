from abc import ABC
import json
from pathlib import Path
from socket import AF_INET, SOCK_STREAM, socket
import tomllib
from typing import Any

from config.config import ServerConfig


class Node(ABC):
  """A device capable of receiving and sending data."""
  header_size: int
  host: str
  port: int
  format: str
  connect_command: str
  disconnect_command: str
  server: socket

  @property
  def address(self) -> tuple[str, int]:
    return self.host, self.port

  def connect(self):
    """Connects to another node."""

  def send_message(self, server: socket, message: dict[str, Any]):
    """Send message."""
    json_message = json.dumps(message)
    encoded_message = json_message.encode()
    self._send_header(server, encoded_message)
    server.send(encoded_message)

  def _send_header(self, server: socket, message: Any):
    """Send message header."""
    header = f"{len(message):<{self.header_size}}"
    server.send(header.encode(self.format))

  def receive_message(self, client: socket) -> dict[str, str]:
    """Return incoming message."""
    header = client.recv(self.header_size).decode()
    buffer_size = int(header)
    response = client.recv(buffer_size)
    message = response.decode()
    return json.loads(message)

  def load_config(self, path: Path):
    with open(path, "rb") as file:
      config = tomllib.load(file)    #type: ignore
      for item in ServerConfig.__annotations__:
        self.__dict__[item] = config[item]    #type: ignore

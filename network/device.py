from abc import ABC
import json
from socket import AF_INET, SOCK_STREAM, socket

from network.config import Config


class Device(ABC):
  """A device capable of receiving and sending data."""
  config: Config
  server: socket = socket(AF_INET, SOCK_STREAM)

  @property
  def server_address(self) -> tuple[str, int]:
    """Returns the server address for clients to connect."""

    return self.config.host, self.config.port

  def connect(self) -> None:
    """Connects to another node."""

  def send_message(self, server: socket, message: dict[str, str]) -> None:
    """Send message."""
    json_message: str = json.dumps(message)
    encoded_message: bytes = json_message.encode()
    self._send_header(server, encoded_message)
    server.send(encoded_message)

  def _send_header(self, server: socket, message: bytes) -> None:
    """Send message header."""
    header: str = f"{len(message):<{self.config.header_size}}"
    server.send(header.encode())

  def receive_message(self, client: socket) -> dict[str, str]:
    """Return incoming message."""
    header: str = client.recv(self.config.header_size).decode()
    buffer_size: int = int(header)
    response: bytes = client.recv(buffer_size)
    message: str = response.decode()
    return json.loads(message)

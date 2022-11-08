from abc import ABC
import json
from pathlib import Path
from socket import AF_INET, SOCK_STREAM, socket

from typing import Any

from network.config import Config

#TODO: Create Connection Address object consisting of IP: Port


class Device(ABC):
  """A device capable of receiving and sending data."""
  config: Config
  server: socket = socket(AF_INET, SOCK_STREAM)

  @property
  def server_address(self) -> tuple[str, int]:
    """Returns the server address for clients to connect."""

    return self.config.host, self.config.port

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
    header = f"{len(message):<{self.config.header_size}}"
    server.send(header.encode())

  def receive_message(self, client: socket) -> dict[str, str]:
    """Return incoming message."""
    header = client.recv(self.config.header_size).decode()
    buffer_size = int(header)
    response = client.recv(buffer_size)
    message = response.decode()
    return json.loads(message)
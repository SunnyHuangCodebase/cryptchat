from __future__ import annotations
import json
from pathlib import Path
import socket
import threading
import time
from typing import Any

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
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(self.address)
    server.listen()
    print(f"[SERVER STARTED] {self.host}:{self.port}")

    while True:
      connection, (ip, port) = server.accept()    # tuple[socket, address]
      thread = threading.Thread(target=self.connect_to_client,
                                args=(connection, ip, port))
      thread.start()
      print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

  def connect_to_client(self, client: socket.socket, ip: str, port: int):
    """Listen for client messages and send responses."""
    while True:
      message = self.receive_message(client)

      if message == self.connect_command:
        print(f"[{ip}:{port}] Connected")
        connected = {
            "Server": self.address,
            "Time": time.time(),
            "Total Online Users": threading.active_count() - 1
        }
        self.send_message(client, connected)
        continue

      if message == self.disconnect_command:
        self.send_message(client, "Disconnected")
        client.close()
        print(f"[{ip}:{port}] Disconnected")
        break

      print(f"[{ip}:{port}] {message}")

      self.send_message(client, message)

  def _send_header(self, client: socket.socket, message: Any):
    """Send message header."""
    header = f"{len(message):<{self.header_size}}"
    client.send(header.encode(self.format))

  def send_message(self, client: socket.socket, message: Any):
    """Send message."""
    json_message = json.dumps(message)
    bytes_message = json_message.encode(self.format)
    self._send_header(client, bytes_message)
    client.send(bytes_message)

  def receive_message(self, client: socket.socket) -> str:
    """Return incoming message."""
    header = client.recv(self.header_size).decode(self.format)
    buffer_size = int(header)
    response = client.recv(buffer_size)
    response = json.loads(response.decode(self.format))
    return str(response)

  def load_config(self, path: Path):
    with open(path, "rb") as file:
      config = tomllib.load(file)    #type: ignore
      for item in ServerConfig.__annotations__:
        self.__dict__[item] = config[item]    #type: ignore


if __name__ == "__main__":
  config_path = Path(__file__).parent / "server_config.toml"
  server = Server(config_path)
  server.start()

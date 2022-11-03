from __future__ import annotations
from pathlib import Path
from socket import socket, AF_INET, SOCK_STREAM
import threading
import time

from devices.node import Node

try:
  import tomllib    #type: ignore
except ModuleNotFoundError:
  import tomli as tomllib    #type: ignore

from message.message_types import MessageType


class ChatServer(Node):
  """Chat server"""
  header_size: int
  host: str
  port: int
  format: str
  connect_command: str
  disconnect_command: str
  chats: dict[str, list[socket]]

  def __init__(self):
    self.server = socket(AF_INET, SOCK_STREAM)
    config_path = Path(__file__).parent / "server_config.toml"
    self.load_config(config_path)
    self.server.bind(self.address)
    self.chats = {}

  @property
  def address(self) -> tuple[str, int]:
    return self.host, self.port

  def start(self):
    """Start the server."""
    self.server.listen()
    print(f"[SERVER STARTED]{self.host}: {self.port}")

    while True:
      connection, (ip, port) = self.server.accept()
      thread = threading.Thread(target=self.connect_to_client,
                                args=(connection, ip, port))
      thread.start()
      print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

  def connect_to_client(self, client: socket, ip: str, port: int):
    """Listen for client messages and send responses."""
    while True:
      message = self.receive_message(client)
      print(message)

      if message["type"] == MessageType.LOGIN:
        print(f"[{ip}:{port}] Connected")

        #TODO: Hash this auth token for security before using it as a chat id.
        auth_token = message["auth_token"]
        #auth_token = self.hash(message["auth_token"])

        self.chats[auth_token] = self.chats.get(auth_token, [])
        self.chats[auth_token].append(client)

        connected = {
            "Server": self.address,
            "Time": time.time(),
            "Chatroom Participants": len(self.chats),
            "auth_token": auth_token,
            "total_online": threading.active_count() - 1,
        }
        self.send_message(client, connected)
        continue

      if message["type"] == MessageType.LOGOUT:
        self.send_message(client, {"status": "Disconnected"})
        client.close()
        print(f"[{ip}:{port}] Disconnected")
        break

      print(f"[{ip}:{port}] {message}")

      #TODO: Send message to all chatroom participants.

      self.send_message(client, message)


if __name__ == "__main__":
  server = ChatServer()
  server.start()

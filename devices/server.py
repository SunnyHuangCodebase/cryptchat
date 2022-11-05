from __future__ import annotations
from pathlib import Path
from socket import socket, AF_INET, SOCK_STREAM
import threading
import time
from devices.config import Config, ServerConfig

from devices.node import Node

try:
  import tomllib    #type: ignore
except ModuleNotFoundError:
  import tomli as tomllib    #type: ignore

from message.message_types import MessageType


class ChatServer(Node):
  """Chat server"""
  config: Config
  chats: dict[str, list[socket]]

  def __init__(self):
    self.config = ServerConfig()
    self.chats = {}
    self.start_server()
    self.await_connections()

  def start_server(self):
    """Start the server."""
    self.server = socket(AF_INET, SOCK_STREAM)
    self.server.bind(self.local_address)
    print(f"[SERVER STARTED] {self.config.host} : {self.config.port}")

  @property
  def local_address(self) -> tuple[str, int]:
    """Returns the local address to start the server."""
    return "", self.config.port

  @property
  def local_host(self) -> tuple[str, int]:
    """Returns localhost:8000 to start the server for debugging."""
    return "localhost", 8000

  @property
  def public_address(self) -> tuple[str, int]:
    return self.config.host, self.config.port

  def await_connections(self):
    """Waits for incoming connections."""
    self.server.listen()

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
      print(f"[{ip}:{port}] {message}")

      if message["type"] == MessageType.LOGIN:
        print(f"[{ip}:{port}] Connected")
        chatroom_id = message["chat_id"]
        status = "New chatroom created" if self.chats.get(
            chatroom_id) else "Joined chatroom"

        self.chats[chatroom_id] = self.chats.get(chatroom_id, [])

        self.chats[chatroom_id].append(client)

        connected = {
            "Server": self.public_address,
            "Time": time.time(),
            "Chatroom Participants": len(self.chats),
            "chat_id": chatroom_id,
            "message": status,
            "total_online": threading.active_count() - 1,
        }
        self.send_message(client, connected)
        continue

      if message["type"] == MessageType.LOGOUT:
        self.send_message(client, {"status": "Disconnected"})
        client.close()
        print(f"[{ip}:{port}] Disconnected")
        break

      if message["type"] == MessageType.MESSAGE:
        chat_id = message["chat_id"]
        for participant in self.chats[chat_id]:
          print(participant)
          self.send_message(
              participant, {
                  "sender": message["sender"],
                  "message": f"{message['sender']}: {message['message']}"
              })


if __name__ == "__main__":
  server = ChatServer()

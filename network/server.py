from __future__ import annotations
from threading import Thread
from threading import active_count as active_threads
from typing import TYPE_CHECKING, Any, NoReturn
from network.config import Config, ServerConfig

from network.device import Device
from chat.message_types import MessageType

if TYPE_CHECKING:
  from socket import socket

#TODO: Create Message object


class ChatServer(Device):
  """Chat server relaying chat messages between authorized clients."""
  config: Config
  chats: dict[str, list[socket]]

  def __init__(self, debug: bool = False) -> None:
    self.config = ServerConfig(debug)
    self.server.bind(self.local_address)
    self.chats = {}

  @property
  def local_address(self) -> tuple[str, int]:
    """Returns the local address to start the server."""
    return "", self.config.port

  def start_server(self) -> NoReturn:
    """Start the server to listen for connections."""
    print(f"[SERVER STARTED] {self.config.host}:{self.config.port}")
    self.server.listen()
    self.await_connections()

  def await_connections(self) -> NoReturn:
    """Waits for incoming connections and starts a thread for each connection."""
    while True:
      connection, (ip, port) = self.server.accept()
      thread: Thread = Thread(target=self.await_messages,
                              args=(connection, ip, port))
      thread.start()
      print(f"[ACTIVE CONNECTIONS] {active_threads() - 1}")

  def await_messages(self, client: socket, ip: str, port: int) -> None:
    """Listens for client messages and sends responses."""
    connected: bool = True
    while connected:
      message: dict[str, str] = self.receive_message(client)
      connected = self.send_response(client, ip, port, message)

  def send_response(self, client: socket, ip: str, port: int,
                    message: dict[str, str]) -> bool:
    """Sends appropriate response to the client based on the user's message."""
    if message["type"] == MessageType.DISCONNECT:
      self.disconnect_user(client, ip, port)
      return False

    chat_id: str = message["chat_id"]
    if message["type"] == MessageType.CONNECT:
      self.assign_chatroom(client, chat_id, ip, port)

    elif message["type"] == MessageType.MESSAGE:
      self.forward_message(message, chat_id)

    return True

  def assign_chatroom(self, client: socket, id: str, ip: str,
                      port: int) -> None:
    """Assigns user to a chatroom with the provided chat ID."""

    print(f"[{ip}:{port}] Connected")
    self.chats[id] = self.chats.get(id, [])
    self.chats[id].append(client)

    status: str = "Joined chatroom." if id in self.chats else "Created chatroom"

    response: dict[str, Any] = {
        "server": self.server_address,
        "participants": len(self.chats),
        "chat_id": id,
        "message": status,
        "total_online": active_threads() - 1,
    }
    self.send_message(client, response)

  def disconnect_user(self, client: socket, ip: str, port: int) -> None:
    """Closes the connection to disconnect user from chat."""
    print(f"[{ip}:{port}] Disconnected")
    client.close()

  def forward_message(self, message: dict[str, str], chat_id: str) -> None:
    """Sends message to all chat particpants."""
    print(f"{message['sender']}: {message['message']}")
    response: dict[str, str] = {
        "sender": message['sender'],
        "message": message['message']
    }
    for recipient in self.chats.get(chat_id, []):
      self.send_message(recipient, response)


if __name__ == "__main__":
  debug: bool = True
  server: ChatServer = ChatServer(debug)
  server.start_server()

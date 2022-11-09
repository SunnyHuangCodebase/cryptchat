from __future__ import annotations
from threading import Thread
from threading import active_count as active_threads
from typing import TYPE_CHECKING, NoReturn

from chat.message import MessageType
from network.config import Config, ServerConfig
from network.connection import ClientConnection, IncomingConnection
from network.device import Device

if TYPE_CHECKING:
  from socket import socket

#TODO: Create Message object


class ChatServer(Device):
  """Chat server relaying chat messages between authorized clients."""
  config: Config
  chats: dict[str, list[socket]]

  def __init__(self, debug: bool = False) -> None:
    self.config = ServerConfig(debug)
    self.chats = {}

  @property
  def local_address(self) -> tuple[str, int]:
    """Returns the local address to start the server."""
    return "", self.config.port

  def start_server(self) -> NoReturn:
    """Start the server to listen for connections."""
    self.server.bind(self.local_address)
    print(f"[SERVER STARTED] {self.config.host}:{self.config.port}")
    self.await_incoming_connections()

  def await_incoming_connections(self) -> NoReturn:
    """Creates a separate thread for each connection to send/receive messages."""
    self.server.listen()
    while True:
      connection: IncomingConnection = self.server.accept()
      client: ClientConnection = ClientConnection(connection)
      thread: Thread = Thread(target=self.await_messages, args=(client,))
      thread.start()
      print(f"[ACTIVE CONNECTIONS] {active_threads() - 1}")

  def await_messages(self, connection: ClientConnection) -> None:
    """Listens for client messages and sends the appropriate response."""
    while True:
      message: dict[str, str] = self.receive_message(connection.client)
      self.send_response(connection, message)

      if message["type"] == MessageType.DISCONNECT:
        break

  def send_response(self, connection: ClientConnection,
                    message: dict[str, str]) -> None:
    """Sends appropriate response to the client based on the user's message."""
    if message["type"] == MessageType.MESSAGE:
      self.send_message_notification(message)

    elif message["type"] == MessageType.CONNECT:
      self.connect_user_to_chat(connection, message)

    elif message["type"] == MessageType.DISCONNECT:
      self.disconnect_user_from_chat(connection)

  def connect_user_to_chat(self, connection: ClientConnection,
                           message: dict[str, str]) -> None:
    """Connect user to a chatroom and notify all partic."""

    print(f"[{connection.ip}:{connection.port}] Connected")

    chat_id: str = message["chat_id"]

    if chat_id in self.chats:
      self.chats[chat_id].append(connection.client)
    else:
      self.chats[chat_id] = [connection.client]

    self.send_join_notification(message)

  def send_join_notification(self, message: dict[str, str]) -> None:
    """Notify users when user joins chatroom."""
    chat_id: str = message["chat_id"]
    notification: dict[str, str] = {
        "sender": "Server",
        "participants": str(len(self.chats[chat_id])),
        "chat_id": chat_id,
        "message": f"{message['sender']} has joined the chatroom.",
        "total_online": str(active_threads() - 1),
    }
    self.send_message_notification(notification)

  def disconnect_user_from_chat(self, connection: ClientConnection) -> None:
    """Disconnects user from chat."""
    print(f"[{connection.ip}:{connection.port}] Disconnected")
    connection.client.close()

  def send_disconnect_notification(self, message: dict[str, str]) -> None:
    """Notify users when user leaves chatroom."""
    chat_id: str = message["chat_id"]
    notification: dict[str, str] = {
        "sender": "Server",
        "participants": str(len(self.chats[chat_id])),
        "chat_id": chat_id,
        "message": f"{message['sender']} has left the chatroom.",
        "total_online": str(active_threads() - 1),
    }
    self.send_message_notification(notification)

  def send_message_notification(self, message: dict[str, str]) -> None:
    """Forwards message notification to all users in a chat."""
    print(f"{message['sender']}: {message['message']}")
    notification: dict[str, str] = {
        "sender": message['sender'],
        "message": message['message']
    }
    for recipient in self.chats.get(message["chat_id"], []):
      self.send_message(recipient, notification)


if __name__ == "__main__":
  debug: bool = True
  server: ChatServer = ChatServer(debug)
  server.start_server()

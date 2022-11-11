from __future__ import annotations
from threading import Thread
from threading import active_count as active_threads
from typing import TYPE_CHECKING, NoReturn

from chat.message import ChatMessage, MessageType, SystemMessage
from network.config import Config, ServerConfig
from network.connection import ClientConnection, IncomingConnection
from network.device import Device

if TYPE_CHECKING:
  from socket import socket


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
      message: SystemMessage | ChatMessage = self.receive_message(
          connection.client)
      self.send_response(connection, message)

      if message.message_type == MessageType.DISCONNECT:
        break

  def send_response(self, connection: ClientConnection,
                    message: SystemMessage | ChatMessage) -> None:
    """Sends appropriate response to the client based on the user's message."""
    if message.message_type == MessageType.MESSAGE:
      self.send_message_notification(message)

    elif message.message_type == MessageType.CONNECT:
      self.connect_user_to_chat(connection, message)

    elif message.message_type == MessageType.DISCONNECT:
      self.disconnect_user_from_chat(connection, message)

  def connect_user_to_chat(self, connection: ClientConnection,
                           message: SystemMessage | ChatMessage) -> None:
    """Connect user to a chatroom and notify all partic."""

    print(f"[{connection.ip}:{connection.port}] {message.sender} connected")
    if message.chat_id in self.chats:
      self.chats[message.chat_id].append(connection.client)
    else:
      self.chats[message.chat_id] = [connection.client]

    self.send_message_notification(message.generate_response())

  def disconnect_user_from_chat(self, connection: ClientConnection,
                                message: SystemMessage | ChatMessage) -> None:
    """Notify users when user leaves chatroom."""
    print(f"[{connection.ip}:{connection.port}]{message.sender} disconnected")
    self.send_message_notification(message.generate_response())

  def send_message_notification(self,
                                message: SystemMessage | ChatMessage) -> None:
    """Forwards message notification to all users in a chat."""
    print(f"{message.sender}: {message.contents}")

    for recipient in self.chats.get(message.chat_id, []):
      self.send_message(recipient, message)


if __name__ == "__main__":
  debug: bool = True
  server: ChatServer = ChatServer(debug)
  server.start_server()

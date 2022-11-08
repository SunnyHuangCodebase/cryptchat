from datetime import datetime, timedelta
from threading import Thread
from typing import Any, NoReturn

from network.config import ClientConfig, Config
from network.device import Device
from chat.message_types import MessageType
from user.user import User
from chat.encryption import KeyGen, PasswordEncryption

#TODO: Add database verification and registration.

DELETE_PREV_LINE: str = "\033[F\033[K"


class ChatClient(Device):
  """Chat client that transmits messages to the server."""
  config: Config
  chatroom: str
  time_zone: timedelta
  user: User
  encryption: PasswordEncryption

  def __init__(self, debug: bool = False) -> None:
    self.config = ClientConfig(debug)
    self.chatroom = ""
    self.time_zone = datetime.now().astimezone().utcoffset() or timedelta(0)

  def connect_to_server(self) -> None:
    """Connects to the server and transmits incoming/outbound messages."""
    self.server.connect(self.server_address)
    self.set_credentials()
    self.join_chatroom()
    Thread(target=self.await_incoming_messages).start()
    self.await_outgoing_messages()

  def set_credentials(self) -> None:
    """Sets attributes based on username, chatroom, and chatroom password input."""
    self.username: str = input("Enter your username: ")
    chatroom: str = input("Enter chatroom name: ")
    password: str = input("Enter chatroom encryption password: ")
    self.encryption: PasswordEncryption = PasswordEncryption(password)
    self.chatroom = KeyGen.generate_hash(chatroom, password).decode()
    print(DELETE_PREV_LINE * 3, end="")

  def join_chatroom(self) -> None:
    """Joins a chatroom with the specified credentials."""
    authentication: dict[str, Any] = {
        "type": MessageType.CONNECT,
        "username": self.username,
        "chat_id": self.chatroom
    }

    self.send_message(self.server, authentication)
    response: dict[str, str] = self.receive_message(self.server)
    print(response["message"])

  def await_incoming_messages(self) -> NoReturn:
    """Listens for incoming messages."""
    while True:
      message: dict[str, str] = self.receive_message(self.server)

      if not message:
        continue
      sender: str = message['sender']
      contents: str = self.encryption.decrypt(message['message'].encode())
      print(f"{sender}: {contents}")

  def await_outgoing_messages(self) -> None:
    """Waits for user messages to send to the server."""
    while True:
      user_input: str = input()
      print(DELETE_PREV_LINE, end="")

      if not user_input:
        continue

      if user_input == self.config.disconnect_command:
        self.send_message(self.server, {"type": MessageType.DISCONNECT})
        break

      message: dict[str, Any] = {
          "type": MessageType.MESSAGE,
          "sender": self.username,
          "chat_id": self.chatroom,
          "message": self.encryption.encrypt(user_input)
      }

      self.send_message(self.server, message)


if __name__ == "__main__":
  debug: bool = True
  client: ChatClient = ChatClient(debug)
  client.connect_to_server()

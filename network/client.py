from datetime import datetime, timedelta
from threading import Thread
from typing import Any, NoReturn

from chat.encryption import KeyGen, PasswordEncryption
from chat.message import MessageType
from network.config import ClientConfig, Config
from network.device import Device
from user.user import User

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
    """Logs user in to the server and transmits incoming/outbound messages."""
    self.login()
    self.await_incoming_messages()
    self.await_outgoing_messages()

  def login(self) -> None:
    """Ask for credentials and send login request to the server."""
    self.request_credentials()
    self.server.connect(self.server_address)
    self.send_login_message()

  def request_credentials(self) -> None:
    """Request username, chatroom, and chatroom password to join a chat."""
    self.username: str = input("Enter your username: ")
    chatroom: str = input("Enter chatroom name: ")
    password: str = input("Enter chatroom encryption password: ")
    self.encryption: PasswordEncryption = PasswordEncryption(password)
    self.chatroom = KeyGen.generate_hash(chatroom, password).decode()
    print(DELETE_PREV_LINE * 3, end="")

  def await_incoming_messages(self) -> None:
    """Creates a thread to display any incoming encrypted messages."""
    thread: Thread = Thread(target=self.display_incoming_messages)
    thread.start()

  def display_incoming_messages(self) -> NoReturn:
    """Listens for incoming messages and displays them in a readable format."""
    while True:
      encrypted_message: dict[str, str] = self.receive_message(self.server)
      message: str = self.decrypt_message(encrypted_message)
      print(message)

  def decrypt_message(self, message: dict[str, str]) -> str:
    """Decrypts an incoming message."""
    sender: str = message['sender']
    contents: str = self.encryption.decrypt(message['message'])
    return f"{sender}: {contents}"

  def await_outgoing_messages(self) -> None:
    """Sends user input as messages to the server."""
    while True:

      user_input: str = input()
      print(DELETE_PREV_LINE, end="")

      if not user_input:
        continue

      if user_input == self.config.disconnect_command:
        self.send_logout_message()
        break

      self.send_chat_message(user_input)

  def send_login_message(self) -> None:
    """Notifies the server of user connecting to the chat."""
    message: dict[str, str] = {
        "type": MessageType.CONNECT,
        "sender": self.username,
        "chat_id": self.chatroom,
        "message": "Connected"
    }
    self.send_message(self.server, message)

  def send_logout_message(self) -> None:
    """Notifies the server of user leaving the chat."""
    message: dict[str, str] = {
        "type": MessageType.DISCONNECT,
        "sender": self.username,
        "chat_id": self.chatroom,
        "message": "Disconnected"
    }
    self.send_message(self.server, message)

  def send_chat_message(self, contents: str) -> None:
    """Sends user's message to the server to forward to chat participants."""
    message: dict[str, str] = {
        "type": MessageType.MESSAGE,
        "sender": self.username,
        "chat_id": self.chatroom,
        "message": self.encryption.encrypt(contents)
    }
    self.send_message(self.server, message)


if __name__ == "__main__":
  debug: bool = True
  client: ChatClient = ChatClient(debug)
  client.connect_to_server()

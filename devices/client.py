from datetime import datetime, timedelta
from pathlib import Path
from socket import socket, AF_INET, SOCK_STREAM
from typing import Any

from devices.node import Node

try:
  import tomllib    #type: ignore
except ModuleNotFoundError:
  import tomli as tomllib    #type: ignore

from config.config import ServerConfig
import threading
from time import sleep
from message.message_types import MessageType
from user.user import User
from message.encryption import KeyGen, PasswordDecryption, PasswordEncryption


class ChatClient(Node):
  """Chat client"""
  header_size: int
  host: str
  port: int
  format: str
  connect_command: str
  disconnect_command: str
  time_zone: timedelta
  chatroom: str
  auth_token: str
  user: User

  def __init__(self):
    self.server = socket(AF_INET, SOCK_STREAM)
    config_path = Path(__file__).parent / "client_config.toml"
    self.load_config(config_path)
    self.time_zone = datetime.now().astimezone().utcoffset() or timedelta(0)
    self.chatroom = ""

  @property
  def server_address(self) -> tuple[str, int]:
    return self.host, self.port

  def listen_for_messages(self):
    """Print any incoming messagse with a 2 second delay timer.

    Does not print messages whose sender and recipient is the same.
    """
    while True:

      message = self.receive_message(self.server)

      if message and message.get("sender") != self.username:
        print(message["message"])

      sleep(2)

  def connect(self):
    """Connect to server."""
    self.server.connect(self.server_address)
    # self.authenticate(self.receive_response(server))

    while not self.chatroom:
      self.join_chatroom()

    thread = threading.Thread(target=self.listen_for_messages)
    thread.start()

    while True:

      message = input(f"{self.username}: ")

      if not message:
        continue

      self.send_message(
          self.server, {
              "type": MessageType.MESSAGE,
              "sender": self.username,
              "chat_id": self.chatroom,
              "message": message
          })

      if message == self.disconnect_command:
        break

  def join_chatroom(self):

    self.username = input("Enter your username: ")
    chatroom = input("Enter chatroom name: ")
    password = input("Enter chatroom encryption password: ")
    self.chatroom = self.generate_chat_id(chatroom, password)

    authentication = {
        "type": MessageType.LOGIN,
        "username": self.username,
        "chat_id": self.chatroom
    }

    self.send_message(self.server, authentication)
    response = self.receive_message(self.server)
    # self.chatroom = response["chat_id"]

  def authenticate(self, response: dict[str, Any]):
    """Verifies user and password hash against server's user database."""
    pass

  def generate_chat_id(self, chat: str, password: str):
    keygen = KeyGen()
    return keygen.generate_hash(chat, password).decode()

  def encrypt_data(self, data: str, password: str) -> str:
    """Encrypts data using a password."""
    encrypter = PasswordEncryption(password)
    return encrypter.encrypt(data).decode()

  def decrypt_data(self, data: bytes, password: str) -> str:
    """Encrypts data using a password."""
    encrypter = PasswordDecryption(password)
    return encrypter.decrypt(data)

  def request_user(self, ip: str):
    message = {"type": MessageType.COMMAND, "target": ip, "message": ip}
    self.send_message(self.server, message)


if __name__ == "__main__":
  client = ChatClient()
  client.connect()

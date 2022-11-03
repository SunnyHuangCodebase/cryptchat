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
from message.message_types import MessageType
from user.user import User
from message.encryption import PasswordEncryption


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

  def connect(self):
    """Connect to server."""
    self.server.connect(self.server_address)
    # self.authenticate(self.receive_response(server))

    while not self.chatroom:
      self.join_chatroom()

    while True:

      message = input()
      if not message:
        continue

      self.send_message(self.server, {
          "type": MessageType.MESSAGE,
          "sender": self.username,
          "message": message
      })

      if message == self.disconnect_command:
        break

      #TODO: Create a separate thread to receive messages with a timeout.
      message = self.receive_message(self.server)

  def join_chatroom(self):

    self.username = input("Enter your username: ")
    self.chatroom = input("Enter chatroom name: ")
    password = input("Enter chatroom encryption password: ")

    authentication = {
        "type":
            MessageType.LOGIN,
        "username":
            self.username,
        "auth_token":
            self.generate_authentication_token(self.chatroom, password)
    }

    self.send_message(self.server, authentication)
    response = self.receive_message(self.server)

    #TODO: chatroom needs to be hashed in server before being resent
    self.chatroom = response["auth_token"]

  def authenticate(self, response: dict[str, Any]):
    """Verifies user and password hash against server's user database."""
    pass

  def generate_authentication_token(self, username: str, password: str) -> str:
    encrypter = PasswordEncryption(password)
    return encrypter.encrypt(username).decode()

  def request_user(self, ip: str):
    message = {"type": MessageType.COMMAND, "target": ip, "message": ip}
    self.send_message(self.server, message)


if __name__ == "__main__":
  client = ChatClient()
  client.connect()

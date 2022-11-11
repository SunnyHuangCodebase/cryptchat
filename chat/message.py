from __future__ import annotations
from abc import ABC, abstractmethod
from enum import auto, Enum

from chat.encryption import Encryption


class MessageType(str, Enum):
  CONNECT = auto()
  DISCONNECT = auto()
  NOTICE = auto()
  MESSAGE = auto()
  COMMAND = auto()
  FILE = auto()

  def __str__(self) -> str:
    return str(self.value)

  def __repr__(self) -> str:
    return str(self.value)


class Message(ABC):
  """An extensible abstract message class."""
  message_type: str
  sender: str
  chat_id: str
  contents: str

  def __init__(self, sender: str, contents: str, chat_id: str) -> None:
    self.sender = sender
    self.contents = contents
    self.chat_id = chat_id

  def jsonify(self) -> dict[str, str]:
    return {
        "type": self.message_type,
        "sender": self.sender,
        "chat_id": self.chat_id,
        "contents": self.contents
    }

  @classmethod
  @abstractmethod
  def from_json(cls, json_message: dict[str, str]) -> Message:
    """Alternate constructor from a json object."""

  @abstractmethod
  def generate_response(self) -> Message:
    """Generate a server response to the message."""


class ChatMessage(Message):

  def __init__(self, sender: str, contents: str, chat_id: str) -> None:
    super().__init__(sender, contents, chat_id)
    self.message_type = MessageType.MESSAGE

  def __str__(self) -> str:
    return f"{self.sender}: {self.contents}"

  @classmethod
  def from_json(cls, json_message: dict[str, str]) -> ChatMessage:
    """Alternate constructor from a json object."""
    return cls(
        json_message["sender"],
        json_message["contents"],
        json_message["chat_id"],
    )

  def generate_response(self) -> ChatMessage:
    """Returns self as the response."""
    return self


class SystemMessage(Message):

  def __init__(self, sender: str, contents: str, chat_id: str,
               message_type: str) -> None:
    super().__init__(sender, contents, chat_id)
    self.message_type = message_type

  @classmethod
  def from_json(cls, json_message: dict[str, str]) -> SystemMessage:
    """Alternate constructor from a json object."""
    return cls(
        json_message["sender"],
        json_message["contents"],
        json_message["chat_id"],
        json_message["type"],
    )

  def generate_response(self) -> SystemMessage:
    """Generate a server response to the message."""

    return SystemMessage(
        "Server",
        f"{self.contents}",
        self.chat_id,
        self.message_type,
    )


class MessageFactory:
  """Generates message objects."""
  username: str
  chatroom: str
  encryption: Encryption

  def __init__(self, username: str, chatroom: str,
               encryption: Encryption) -> None:
    self.username = username
    self.chatroom = chatroom
    self.encryption = encryption

  @staticmethod
  def from_json(json_message: dict[str, str]) -> SystemMessage | ChatMessage:
    """Generates a message object from json_message"""

    message_type = json_message["type"]

    if message_type in (MessageType.CONNECT, MessageType.DISCONNECT):
      return SystemMessage.from_json(json_message)

    return ChatMessage.from_json(json_message)

  def generate_login_message(self) -> SystemMessage:
    return SystemMessage(
        self.username,
        self.encryption.encrypt(f"{self.username} connected"),
        self.chatroom,
        MessageType.CONNECT,
    )

  def generate_logout_message(self) -> SystemMessage:
    return SystemMessage(
        self.username,
        self.encryption.encrypt(f"{self.username} disconnected"),
        self.chatroom,
        MessageType.DISCONNECT,
    )

  def generate_message(self, message: str) -> ChatMessage:
    return ChatMessage(
        self.username,
        self.encryption.encrypt(message),
        self.chatroom,
    )

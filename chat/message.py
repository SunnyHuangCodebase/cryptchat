from __future__ import annotations
from abc import ABC, abstractmethod
from enum import auto, Enum
from typing import Self

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

  def __init__(self, sender: str, contents: str, chat_id: str):
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
  def from_json(cls, json: dict[str, str]) -> Self:
    """Alternate constructor from a json object."""


class ChatMessage(Message):

  def __init__(self, sender: str, contents: str, chat_id: str) -> None:
    super().__init__(sender, contents, chat_id)
    self.message_type = MessageType.MESSAGE

  def __str__(self) -> str:
    return f"{self.sender}: {self.contents}"

  @classmethod
  def from_json(cls, json: dict[str, str]) -> Self:
    """Alternate constructor from a json object."""
    return cls(
        json["sender"],
        json["contents"],
        json["chat_id"],
    )


class SystemMessage(Message):

  def __init__(self, sender: str, contents: str, chat_id: str,
               message_type: str) -> None:
    super().__init__(sender, contents, chat_id)
    self.message_type = message_type

  @classmethod
  def from_json(cls, json: dict[str, str]) -> Self:
    """Alternate constructor from a json object."""
    return cls(
        json["sender"],
        json["contents"],
        json["chat_id"],
        json["type"],
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

  def generate_login_message(self) -> SystemMessage:
    return SystemMessage(
        self.username,
        "Connected",
        self.chatroom,
        MessageType.CONNECT,
    )

  def generate_logout_message(self) -> SystemMessage:
    return SystemMessage(
        self.username,
        "Disconnected",
        self.chatroom,
        MessageType.DISCONNECT,
    )

  def generate_message(self, message: str) -> ChatMessage:
    return ChatMessage(
        self.username,
        self.encryption.encrypt(message),
        self.chatroom,
    )

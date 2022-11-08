from enum import auto, Enum


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

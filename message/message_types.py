from enum import auto, Enum


class MessageType(str, Enum):
  LOGIN = auto()
  LOGOUT = auto()
  NOTICE = auto()
  MESSAGE = auto()
  JOIN = auto()
  COMMAND = auto()
  FILE = auto()

  def __str__(self) -> str:
    return str(self.value)

  def __repr__(self) -> str:
    return str(self.value)

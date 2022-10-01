from typing import TypedDict


class ServerConfig(TypedDict):
  header_size: int
  host: str
  port: int
  format: str
  connect_command: str
  disconnect_command: str

from http.client import HTTPResponse
from pathlib import Path
from socket import socket, gethostbyname
from typing import Protocol, TypedDict
from urllib.request import urlopen

try:
  import tomllib    #type: ignore
except ModuleNotFoundError:
  import tomli as tomllib    #type: ignore


class Config(Protocol):
  header_size: int
  host: str
  port: int
  connect_command: str
  disconnect_command: str


class ServerConfig:
  """Initializes Server settings."""
  header_size: int = 16
  host: str
  port: int = 5190
  connect_command: str = "/connect"
  disconnect_command: str = "/disconnect"

  def __init__(self):
    self.host = self.get_public_ip()

  def get_public_ip(self):
    """Sets host to public IP address."""
    ip: HTTPResponse = urlopen("https://api.ipify.org/?format=raw")
    return ip.readline().decode()


class ClientConfig:
  """Initializes Client settings."""
  header_size: int = 16
  host: str = "71.245.250.47"
  port: int = 5190
  connect_command: str = "/connect"
  disconnect_command: str = "/disconnect"

  @classmethod
  def with_domain_host(cls, domain: str):
    """Alternate constructor setting host to a domain's public IP address."""
    self = cls()
    self.host = gethostbyname(domain)
    return self

  @classmethod
  def with_local_host(cls):
    self = cls()
    self.host = "localhost"
    self.port = 8000


if __name__ == "__main__":
  pass

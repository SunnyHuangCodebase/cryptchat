from http.client import HTTPResponse
from socket import gethostbyname
from typing import Protocol, Self
from urllib.request import urlopen


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

  def __init__(self, debug=False) -> None:
    if debug:
      self.host = "localhost"
      self.port = 8000
    else:
      self.host = self.get_public_ip()

  def get_public_ip(self) -> str:
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

  def __init__(self, debug: bool = False) -> None:
    if debug:
      self.host = "localhost"
      self.port = 8000

  @classmethod
  def with_domain_host(cls, domain: str) -> "ClientConfig":
    """Alternate constructor setting host to a domain's public IP address."""
    self = cls()
    self.host = gethostbyname(domain)
    return self


if __name__ == "__main__":
  pass

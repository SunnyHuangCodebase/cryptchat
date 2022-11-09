from socket import socket

Address = tuple[str, int]
IncomingConnection = tuple[socket, Address]


class ClientConnection:
  """Represents a server-client connection with client details. """
  client: socket
  ip: str
  port: int

  def __init__(self, connection: IncomingConnection) -> None:
    self.client, (self.ip, self.port) = connection

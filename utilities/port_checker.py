import socket
import threading
from time import sleep

host = socket.gethostbyname(socket.gethostname())


class Port(int):
  """A port is an integer that cannot be less than 0."""
  number: int

  def __new__(cls, number: int):
    return max(0, number)


def check_port(port: int, timeout: float):
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    try:
      server.settimeout(timeout)
      server.connect((host, port))
      ports_in_use.add(port)

    except socket.error:
      available_ports.add(port)


def check_open_ports(start: int, end: int | None = None, timeout: float = 0.1):

  if not end:
    check_port(Port(start), timeout)
    return

  port_range = range(Port(start), Port(end + 1))

  for port in port_range:
    print(f"Checking port {port}")
    thread = threading.Thread(target=check_port, args=(port, timeout))
    thread.start()

  sleep(timeout + 0.1)


if __name__ == "__main__":

  ports_in_use: set[int] = set()
  available_ports: set[int] = set()

  check_open_ports(5190)
  check_open_ports(0, 100)
  print(f"{ports_in_use=}")
  print(f"{available_ports=}")

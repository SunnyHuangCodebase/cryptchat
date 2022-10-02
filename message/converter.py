import json
import pickle
from typing import Any, Protocol

FORMAT = "UTF-8"


class MessageConverter(Protocol):
  """A protocol for converting data between two formats.

    One format should be compatible with network transmission.
    The other format should be usable by the app.
  """

  def serialize(self, data: Any) -> bytes:
    """Translates data into a format transmittable over TCP."""
    ...

  def deserialize(self, data: bytes) -> Any:
    """Reverts serialized data to the format usable by the app."""
    ...


class StringByteConverter:
  """Converts data between string and byte format."""

  def serialize(self, data: str) -> bytes:
    """Converts string to bytes."""
    return data.encode(FORMAT)

  def deserialize(self, data: bytes) -> str:
    """Converts bytes to string."""
    return data.decode(FORMAT)


class JSONByteConverter:
  """Converts data between JSON-compatible and byte format."""

  def serialize(self, data: dict[Any, Any]) -> bytes:
    """Converts string to bytes."""
    return json.dumps(data).encode(FORMAT)

  def deserialize(self, data: bytes) -> dict[Any, Any]:
    """Converts bytes to string."""
    return json.loads(data.decode(FORMAT))


class PickleByteConverter:
  """Converts data between object and byte format.

  WARNING: Deserializing pickled data can execute malicious code.
  Only deserialize pickled data from a trusted source.
  """

  def serialize(self, data: Any) -> bytes:
    """Converts object to bytes."""
    return pickle.dumps(data)

  def deserialize(self, data: bytes) -> Any:
    """Converts bytes to string."""
    return pickle.loads(data)

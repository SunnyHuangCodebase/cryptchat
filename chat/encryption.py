import base64

from pathlib import Path
from typing import Callable, Protocol
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Encrypter(Protocol):

  def encrypt(self, string: str) -> str:
    ...


class Decrypter(Protocol):

  def decrypt(self, string: bytes) -> str:
    ...


class StoredKeyEncryption:
  path: Path = Path("encryption.key")
  key: bytes

  def __init__(self) -> None:
    self.key = self.load_key() or self.create_key()
    self.save_key()

  def load_key(self) -> bytes | None:
    """Loads an encryption key if it exists."""
    with open(self.path, "rb") as file:
      return file.read()

  def create_key(self) -> bytes:
    """Creates an encryption key."""
    return Fernet.generate_key()

  def save_key(self) -> None:
    """Saves the key"""
    with open(self.path, "rb+") as file:
      file.write(self.key)

  def encrypt(self, message: str) -> str:
    """Encrypts a message using a key stored in a key file."""
    encoded_message: bytes = message.encode()
    fernet: Fernet = Fernet(self.key)
    return fernet.encrypt(encoded_message).decode()


class StoredKeyDecryption:
  path: Path = Path("encryption.key")
  key: bytes

  def __init__(self) -> None:
    key: bytes | None = self.load_key()

    if not key:
      raise Exception("No Encryption Key")

    self.key = key

  def load_key(self) -> bytes | None:
    """Loads an encryption key if it exists."""
    with open(self.path, "rb") as file:
      return file.read()

  def decrypt(self, encrypted_message: str) -> str:
    """Decrypts a message using a key stored in a key file."""
    fernet: Fernet = Fernet(self.key)
    encoded_message: bytes = fernet.decrypt(encrypted_message)
    return encoded_message.decode()


class KeyGen:
  """A key generator to provide a hash key based on provided password and salt."""

  @staticmethod
  def generate_hash(data: str = "", salt_string: str = "") -> bytes:
    """Generate a key from provided password and salt."""
    if not data:
      data = input()

    if not salt_string:
      salt: bytes = b'\xde\xe04\xd7\xeb\xd04\xd7ah\xa8\x8e\xa5\xb1\xe9>'
    else:
      salt = salt_string.encode()
    kdf: PBKDF2HMAC = PBKDF2HMAC(algorithm=hashes.SHA256(),
                                 length=32,
                                 salt=salt,
                                 iterations=480000,
                                 backend=default_backend())

    return base64.urlsafe_b64encode(kdf.derive(data.encode()))


class PasswordEncryption:
  encrypter: Fernet

  def __init__(self, password: str) -> None:
    key: bytes = KeyGen.generate_hash(password)
    self.encrypter = Fernet(key)

  def encrypt(self, message: str) -> str:
    """Encrypts a message from a key generated from a password."""
    return self.encrypter.encrypt(message.encode()).decode()

  def decrypt(self, encrypted_message: bytes) -> str:
    """Decrypts a message from a key generated from a password."""
    return self.encrypter.decrypt(encrypted_message).decode()


def encrypt(encrypter: Encrypter) -> Callable[[str], str]:
  """Encryption decorator. Encrypts text using a secret key."""

  def wrapper(message: str) -> str:
    return encrypter.encrypt(message)

  return wrapper


def decrypt(decrypter: Decrypter) -> Callable[[bytes], str]:
  """Decryption decorator. Decrypts text using a secret key."""

  def wrapper(message: bytes):
    return decrypter.decrypt(message)

  return wrapper


if __name__ == "__main__":
  # e: KeyGen = KeyGen()
  # for i in range(10):
  #   encrypted: bytes = e.generate_hash("Chatroom", "password")
  #   print(encrypted)

  e: PasswordEncryption = PasswordEncryption("password")
  encrypted: str = e.encrypt("some_string")
  print(encrypted)
  decrypted: str = e.decrypt(encrypted.encode())
  print(decrypted)
  print(decrypted.encode())

  # decrypted = d.decrypt(encrypted)
  # print(decrypted)
  # print(e.encrypt("a"))
  # print(d.generate_key("a"))

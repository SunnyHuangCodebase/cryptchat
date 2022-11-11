import base64

from pathlib import Path
from typing import Callable, Protocol
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Encryption(Protocol):
  """A protocol that has encrypt and decrypt methods."""

  def encrypt(self, data: str) -> str:
    ...

  def decrypt(self, data: str) -> str:
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

  def encrypt(self, data: str) -> str:
    """Encrypts data using a key stored in a key file."""
    fernet: Fernet = Fernet(self.key)
    return fernet.encrypt(data.encode()).decode()

  def decrypt(self, data: str) -> str:
    """Decrypts data using a key stored in a key file."""
    fernet: Fernet = Fernet(self.key)
    decrypted: bytes = fernet.decrypt(data)
    return decrypted.decode()


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
  """Encrypts data using a hash key generated from a password."""
  encrypter: Fernet

  def __init__(self, password: str) -> None:
    key: bytes = KeyGen.generate_hash(password)
    self.encrypter = Fernet(key)

  def encrypt(self, data: str) -> str:
    """Encrypts data from a key generated from a password."""
    return self.encrypter.encrypt(data.encode()).decode()

  def decrypt(self, data: str) -> str:
    """Decrypts data from a key generated from a password."""
    return self.encrypter.decrypt(data.encode()).decode()


def encrypt(encrypter: Encryption) -> Callable[[str], str]:
  """Encryption decorator. Encrypts text using a secret key."""

  def wrapper(data: str) -> str:
    return encrypter.encrypt(data)

  return wrapper


def decrypt(decrypter: Encryption) -> Callable[[str], str]:
  """Decryption decorator. Decrypts text using a secret key."""

  def wrapper(data: str) -> str:
    return decrypter.decrypt(data)

  return wrapper

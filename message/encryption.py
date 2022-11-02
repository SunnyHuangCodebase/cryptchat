import base64

from pathlib import Path
from typing import Protocol
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Encrypter(Protocol):

  def encrypt(self, string: str) -> bytes:
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

  def save_key(self):
    """Saves the key"""
    with open(self.path, "rb+") as file:
      file.write(self.key)

  def encrypt(self, message: str):
    """Encrypts a message using a key stored in a key file."""
    encoded_message = message.encode()
    fernet = Fernet(self.key)
    return fernet.encrypt(encoded_message)


class StoredKeyDecryption:
  path = Path("encryption.key")
  key: bytes

  def __init__(self) -> None:
    key = self.load_key()

    if not key:
      raise Exception("No Encryption Key")

    self.key = key

  def load_key(self) -> bytes | None:
    """Loads an encryption key if it exists."""
    with open(self.path, "rb") as file:
      return file.read()

  def decrypt(self, encrypted_message: str):
    """Decrypts a message using a key stored in a key file."""
    fernet = Fernet(self.key)
    encoded_message = fernet.decrypt(encrypted_message)
    return encoded_message.decode()


class KeyGen:
  """A key generator to provide a key based on a password."""

  def generate_key(self) -> bytes:
    """Generate a key from inputted password."""
    password_input = input()
    password = password_input.encode()
    salt = b'\xde\xe04\xd7\xeb\xd04\xd7ah\xa8\x8e\xa5\xb1\xe9>'
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=32,
                     salt=salt,
                     iterations=100000,
                     backend=default_backend())

    return base64.urlsafe_b64encode(kdf.derive(password))


class PasswordEncryption:
  key: bytes

  def __init__(self):
    keygen = KeyGen()
    self.key = keygen.generate_key()

  def encrypt(self, message: str) -> bytes:
    """Encrypts a message from a key generated from a password."""
    encoded_message = message.encode()
    fernet = Fernet(self.key)
    return fernet.encrypt(encoded_message)


class PasswordDecryption:
  key: bytes

  def __init__(self):
    keygen = KeyGen()
    self.key = keygen.generate_key()

  def decrypt(self, encrypted_message: bytes) -> str:
    """Decrypts a message from a key generated from a password."""
    fernet = Fernet(self.key)
    encoded_message = fernet.decrypt(encrypted_message)
    return encoded_message.decode()


def encrypt(encrypter: Encrypter):
  """Encryption decorator. Encrypts text using a secret key."""

  def wrapper(message: str):
    return encrypter.encrypt(message)

  return wrapper


def decrypt(decrypter: Decrypter):
  """Decryption decorator. Decrypts text using a secret key."""

  def wrapper(message: bytes):
    return decrypter.decrypt(message)

  return wrapper
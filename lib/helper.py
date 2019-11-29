import binascii
import hashlib
import json
import os
from uuid import uuid4

GAS_PRICE = 0.001

class Helper:
  @staticmethod
  def hash_data(data: bytes) -> str:
    hash_id = hashlib.sha256()
    hash_id.update(data)
    return str(hash_id.hexdigest())

  @staticmethod
  def generate_address() -> str:
    return binascii.hexlify(os.urandom(16)).decode()

  @staticmethod
  def object_to_bytes(obj: dict) -> bytes:
    return json.dumps(obj).encode('utf-8')

  @staticmethod
  def bytes_to_object(data: bytes) -> dict:
    return json.load(data.decode('utf-8'))

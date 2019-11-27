import hashlib
import json
from uuid import uuid4

class Helper:
  @staticmethod
  def hash_data(data: bytes) -> str:
    hash_id = hashlib.sha256()
    hash_id.update(data)
    return str(hash_id.hexdigest())

  @staticmethod
  def generate_address() -> str:
    return uuid4().hex

  @staticmethod
  def object_to_bytes(obj: dict) -> bytes:
    return json.dumps(obj).encode('utf-8')

  @staticmethod
  def bytes_to_object(self, data: bytes) -> dict:
    return json.load(data.decode('utf-8'))

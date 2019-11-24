import hashlib
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

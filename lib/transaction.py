import time
from typing import Any
from lib.helper import Helper
from lib.crypto import Crypto

class Transaction:
  def __init__(
    self,
    amount: float = None,
    data: Any = None,
    gas_limit: float = None,
    gas_price: float = None,
    nonce: int = 0,
    recipient: str = None,
    sender: str = None,
    signature: str = None,
    hash: str = None
  ):
    self.amount: float = amount
    self.data: Any = data
    self.gas_limit: float = gas_limit
    self.gas_price: float = gas_price
    self.nonce: int = nonce
    self.recipient: str = recipient
    self.sender = sender
    self.signature: str = signature
    self.hash: str = None

  def set_nonce(self, nonce: int):
    self.nonce = nonce
    
  def get_sender(self) -> str:
    return self.sender

  def set_sender(self, sender: str):
    self.sender = sender

  def get_signature(self) -> str:
    return self.signature

  def set_signature(self, signature: str):
    self.signature = signature

  def get_recipient(self) -> str:
    return self.recipient

  def set_recipient(self, recipient: str):
    self.recipient = recipient

  def get_amount(self) -> float:
    return self.amount

  def set_amount(self, amount: float):
    self.amount = amount

  def set_gas_price(self, gas_price: float):
    self.gas_price = gas_price

  def get_gas_price(self) -> float:
    return self.gas_price

  def set_data(self, data: Any):
    self.data = data

  def get_data(self) -> Any:
    return self.data

  def set_gas_limit(self, gas_limit):
    self.gas_limit = gas_limit

  def get_gas_limit(self) -> float:
    return self.gas_limit

  def get_nonce(self) -> int:
    return self.nonce

  def get_body(self) -> bytes:
    return self.__dict__

  def set_hash(self, _hash: str):
    self.hash = _hash

  def get_hash(self) -> str: 
    return self.hash
  
  def get_transaction_data(self) -> dict:
    return {
      'amount': self.get_amount(),
      'data': self.get_data(),
      'gas_limit': self.get_gas_limit(),
      'gas_price': self.get_gas_price(),
      'hash': self.get_hash(),
      'nonce': self.get_nonce(),
      'recipient': self.get_recipient(),
      'sender': self.get_sender(),
    }

  def sign_transaction(self, private_key: str):
    context = self.get_transaction_data()
    signature = Crypto.sign(context, private_key)
    self.set_signature(signature)

  def verify_signature(self, public_key: str) -> bool:
    context = self.get_transaction_data()
    return Crypto.verify(context, self.get_signature(), public_key)

  def hash_transaction(self) -> str:
    context = self.get_transaction_data()
    context.update({'signature': self.get_signature()})
    return Helper.hash_data(Helper.object_to_bytes(context))

  @staticmethod
  def make_transaction(transaction_data: dict):
    return Transaction(
      amount=transaction_data['amount'],
      data=transaction_data['data'],
      gas_limit=transaction_data['gas_limit'],
      gas_price=transaction_data['gas_price'],
      hash=transaction_data['hash'],
      nonce=transaction_data['nonce'],
      recipient=transaction_data['recipient'],
      sender=transaction_data['sender'],
      signature=transaction_data['signature'],
    )

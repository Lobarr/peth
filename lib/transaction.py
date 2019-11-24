import time
from typing import Any
from .helper import Helper

class Transaction:

  def __init__(
    self, 
    amount: float = None, 
    data: Any = None,
    gas_limit: int = None, 
    gas_price: float = None, 
    nonce: int = None,
    recipient: str = None, 
    sender: str = None, 
    signature: str = None, 
    start_gas: float = None
  ):
    self.amount: float = amount
    self.data: Any = data
    self.gas_limit: int = gas_limit
    self.gas_price: float = gas_price
    self.nonce: int = nonce
    self.recipient: str = recipient
    self.sender = sender
    self.signature: str = signature
    self.start_gas: float = start_gas

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

  def set_start_gas(self, start_gas: float):
    self.start_gas = start_gas

  def get_start_gas(self) -> float:
    return self.start_gas
  
  def set_data(self, data: Any):
    self.data = data

  def get_data(self) -> Any:
    return self.data

  def _get_data_bytes(self) -> bytes:
    return repr({
      'amount': self.get_amount(),
      'data': self.get_data(),
      'gas_price': self.get_gas_price(),
      'recipient': self.get_recipient(),
      'signature': self.get_signature(),
      'start_gas': self.get_start_gas(),
    }).encode('utf-8')

  def sign_transaction(self, private_key: str):
    pass

  def get_body(self) -> dict:
    return self.__dict__

  @staticmethod
  def make_transaction(transaction_data: dict):
    return Transaction(
      amount=transaction_data['amount'],
      gas_price=transaction_data['gas_price'],
      data=transaction_data['data'],
      recipient=transaction_data['recipient'],
      signature=transaction_data['signature'],
      start_gas=transaction_data['start_gas']
    )

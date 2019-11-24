from typing import Any

class Message:
  def __init__(self, sender: str = None, recipient: str = None, amount: float = None, data: Any = None):
    self.sender: str = sender
    self.recipient: str = recipient
    self.amount: float = amount
    self.data: Any = data
    self.start_gas
  
  def get_recipient(self) -> str:
    return self.to_address

  def set_recipient(self, recipient: str):
    self.recipient = recipient

  def get_amount(self) -> float:
    return self.amount

  def set_amount(self, amount: float):
    self.amount = amount

  def set_data(self, data: Any):
    self.data = data

  def get_data(self) -> Any:
    return self.data

  def set_start_gas(self, start_gas: float):
    self.start_gas = start_gas

  def get_start_gas(self) -> float:
    return self.start_gas

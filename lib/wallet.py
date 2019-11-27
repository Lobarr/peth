import binascii
import os
from .account import Account
from .crypto import Crypto

class Wallet:
  def __init__(self, address: str = None):
    private_key, public_key = Crypto.generate_key_pair()
    self.address = str = address
    self.private_key: str = private_key
    self.public_key: str = public_key

  def get_public_key(self):
    return self.public_key
  
  def set_public_key(self, public_key: str):
    self.public_key = public_key

  def get_private_key(self):
    return self.private_key

  def set_private_key(self, private_key: str):
    self.private_key = private_key

  def get_address(self):
    return self.address

  def set_address(self, address: int):
    self.address = address

  def get_data(self) -> dict:
    return self.__dict__

  def get_summary(self, account: Account) -> dict:
    return {
      'address': self.get_address(),
      'public_key': self.get_public_key(),
      'balance': account.get_balance(),
    }



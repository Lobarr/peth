import binascii
import os
from .account import Account

WALLET_KEY_SIZE = 8

class Wallet:
  def __init__(self, address: str = None):
    self.public_key: str = binascii.b2a_hex(os.urandom(WALLET_KEY_SIZE)).decode('utf-8')
    self.private_key: str = binascii.b2a_hex(os.urandom(WALLET_KEY_SIZE)).decode('utf-8')
    self.address = str = address

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
      'public_key': self.get_public_key(),
      'address': self.get_address(),
      'balance': account.get_balance()
    }



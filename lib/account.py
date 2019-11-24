from copy import deepcopy
from .helper import Helper
from .transaction import Transaction
from .message import Message

DEFAULT_BALANCE = 10.0
class Account:

  def __init__(self, address: str = None, nonce: int = None, balance: float = DEFAULT_BALANCE, contract_code: str = None, state: dict = None):
    self.address: str = address
    self.nonce: int = nonce
    self.balance: float = balance
    self.contract_code: str = contract_code
    self.contract_hash: str = None
    self.state_root: dict = state

  def set_address(self, address: str):
    self.address = address

  def get_address(self) -> str:
    return self.address
  
  def set_nonce(self, nonce: int):
    self.nonce = nonce

  def get_nonce(self) -> int:
    return self.nonce

  def set_balance(self, balance: float):
    self.balance = balance

  def get_balance(self) -> float:
    return self.balance

  def set_contract_code(self, contract_code: str):
    self.contract_code = contract_code
    self.contract_hash = Helper.hash_data(contract_code.encode('utf-8'))

  def get_contract_code(self) -> str:
    return self.contract_code

  def set_state(self, state: dict):
    self.state = state

  def get_state(self) -> dict:
    return self.state

  def is_contract(self):
    return self.contract_code != None

  def deposit(self, amount: int):
    self.balance += amount

  def withdraw(self, amount: int) -> bool:
    if self.balance > amount:
      self.balance -= amount
      return True
    return False

  def modify_state(self, modified_state: dict):
    self.state.update(modified_state)

  def exec_contract(self, message: Message):
    #! contracts can access and modify state by declaring globally
    state = deepcopy(self.get_state())
    if self.is_contract():
      compiled_contract = compile(self.get_contract_code(), self.get_address(), 'exec')
      injected_context = {
        'state': state,
        'data': message.get_data()
      }
      exec(compiled_contract, injected_context)
      self.modify_state(state)

  def verify_balance(self, message: Message):
    # fee = message.
    pass

  def transition_state(self, message: Message):
    if not self.verify_balance():
      raise Exception('insufficient gas')
    self.exec_contract(message)


  def get_body(self) -> dict:
    return self.__dict__

  @staticmethod
  def make_account(account_data: dict):
    return Account(
      address=account_data['address'],
      nonce=account_data['nonce']+1,
      balance=account_data['balance'],
      contract_code=account_data['contract_code'],
      state=account_data['state']
    )



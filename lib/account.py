from copy import deepcopy
from .helper import Helper
from .transaction import Transaction

DEFAULT_BALANCE = 10.0
class Account:

  def __init__(self, address: str = Helper.generate_address(), balance: float = DEFAULT_BALANCE, contract_code: str = None, contract_hash: str = None, state: dict = {}):
    self.address: str = address
    self.balance: float = balance
    self.contract_code: str = contract_code
    self.contract_hash: str = contract_hash
    self.state: dict = state

  def set_address(self, address: str):
    self.address = address

  def get_address(self) -> str:
    return self.address


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

  def calc_gas(self) -> float:
    # returns gas required to execute contract
    pass

  def charge_gas(self, gas: float) -> bool:
    # take gas needed to execute contract, return true if successful or false if not
    return True

  def modify_state(self, modified_state: dict):
    self.state.update(modified_state)

  def exec_contract(self, transaction: Transaction):
    #! contracts can access and modify state, transaction data field and msg object by declaring globally
    new_state = deepcopy(self.get_state())
    if self.is_contract():
      compiled_contract = compile(self.get_contract_code(), self.get_address(), 'exec')
      injected_context = {
        'state': new_state,
        'data': transaction.get_data(),
        'msg': {
          'sender': transaction.get_sender(),
          'nonce': transaction.get_nonce()
        }
      }
      exec(compiled_contract, injected_context)
      self.modify_state(new_state)

  def get_body(self) -> dict:
    return self.__dict__

  @staticmethod
  def make_account(account_data: dict):
    return Account(
      address=account_data['address'],
      balance=account_data['balance'],
      contract_code=account_data['contract_code'],
      contract_hash=account_data['contract_hash'],
      state=account_data['state']
    )



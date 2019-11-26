import dis
from copy import deepcopy
from io import StringIO

from .helper import Helper
from .message import Message
from .transaction import Transaction

DEFAULT_BALANCE = 10.0
class Account:

  def __init__(self, address: str = "", nonce: int = 0, balance: float = DEFAULT_BALANCE, contract_code: str = "", state: dict = {}):
    self.address: str = address
    self.nonce: int = nonce
    self.balance: float = balance
    self.contract_code: str = self.set_contract_code(contract_code)
    self.contract_hash: str = None
    self.state_root: dict = state
    self.funcs = {}

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

  def set_contract_code(self, contract_code: str) -> bool:
    # Compiled(co) contract code 
    # Will only be set it there passes all validation
    # Returns true if set otherwise false

    # Security check to ensure code is clean
    security_clearance: bool = True if self.is_contract_clean(contract_code) else False

    self.contract_code = contract_code if security_clearance == True else ""
    self.contract_hash = Helper.hash_data(self.contract_code.encode('utf-8'))

    if security_clearance:
      self.generateFunctions(self.contract_code)

    return security_clearance

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
  
  def is_contract_clean(self, contract_code: str) -> bool:
    # Compile and disassemble the contract code
    co_contract_code = compile(contract_code, self.get_address(), 'exec')
    dis.dis(co_contract_code, file=open('temp_disassemble', 'w'))
    
    disassembly = open('temp_disassemble', 'r').read().split()

    # Blacklisted codes
    blacklist = ['IMPORT_NAME', '(exec)', '(eval)', '(compile)']

    # Return false if there are any blacklisted options
    if any(check in disassembly for check in blacklist):
      return False
    
    return True
  
  def generateFunctions(self, contract_code: str) -> list:
    co_contract_code = compile(contract_code, 'temp_compile', 'exec')
    # Extracts the functions by checking their type after compilation
    # functions will have code object type instead of a string
    _extracted_funcs = [constant for constant in co_contract_code.co_consts if type(constant) == type(compile('', '', 'exec'))]
    self.funcs = {str(func.co_name): func for func in _extracted_funcs}

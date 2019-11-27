import base64
from contextlib import redirect_stdout
from copy import deepcopy
from dis import dis
from io import StringIO

from .helper import Helper
from .transaction import Transaction

DEFAULT_BALANCE = 10.0
GAS_PRICE = 1/1000

class Account:

  def __init__(self, address: str = Helper.generate_address(), balance: float = DEFAULT_BALANCE, contract_code: str = None, contract_hash: str = None, state: dict = {}):
    self.address: str = address
    self.balance: float = balance
    self.contract_code: str = contract_code
    self.contract_hash: str = contract_hash
    self.state: dict = state

    # Funcs will the actual funcs that can be called
    # ex. self.funcs['myfunction'](<parameters>)
    self.funcs = {}
    # Funcs args are a list a arguments that stored for a given function,
    # parameters names are stored as str in a tuple
    # ex. self.funcs_args['myfunction'] -> will return (<parameter1_name>, <parameter2_name>)
    self.funcs_args = {}

  def set_address(self, address: str):
    self.address = address

  def get_address(self) -> str:
    return self.address


  def set_balance(self, balance: float):
    self.balance = balance

  def get_balance(self) -> float:
    return self.balance

  def set_contract_code(self, contract_code: str) -> bool:
    # Compiled(co) contract code 
    # Will only be set it there passes all validation
    # Returns true if set otherwise false

    # Decode the contract code 
    code = str(base64.urlsafe_b64decode(contract_code).decode())
    # Security check to ensure code is clean    
    security_clearance: bool = True if self.is_contract_clean(code) else False

    self.contract_code = code if security_clearance == True else ""
    if security_clearance:
      self.contract_hash = Helper.hash_data(self.contract_code.encode())

    if security_clearance:
      self.generateFunctions(self.contract_code)
    print(security_clearance)
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

  def calc_gas(self, func_name: str) -> float:
    # calculates the gas cost
    if func_name in self.funcs:
      # Redirect the disassemble to a buffer
      buffer = StringIO()
      with redirect_stdout(buffer):
        dis(self.funcs[func_name])
      
      # Get the value of disassemble
      disassemble = buffer.getvalue()

      # calculate the number of instructions
      num_of_instructions = len(disassemble.split('\n'))

      # Gas is equal to the number of instructions that need to be executed
      return num_of_instructions * GAS_PRICE

    return 0

  def charge_gas(self, gas: float, func_name: str, func_args: tuple) -> bool:
    try:
      if func_name in self.funcs:
        # Unwrap the function arguments from the tuple and pass them to the function
        if self.calc_gas(func_name) < gas:
          self.funcs[func_name](*func_args)
        # Return true indicating the function has been executed and gas has been charged
        return True
    except:
      # Return false if the gas has not been charged and function has not been executed
      return False
    
    return False

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
    # Remove functions for export
    body: dict = deepcopy(self.__dict__)
    body['funcs'] = [key for key in body['funcs'].keys()]
    return body

  @staticmethod
  def make_account(account_data: dict):
    return Account(
      address=account_data['address'],
      balance=account_data['balance'],
      contract_code=account_data['contract_code'],
      contract_hash=account_data['contract_hash'],
      state=account_data['state']
    )
  
  def is_contract_clean(self, contract_code: str) -> bool:
    # Compile and disassemble the contract code
    co_contract_code = compile(contract_code, self.get_address(), 'exec')
    dis(co_contract_code, file=open('temp_disassemble', 'w'))
    
    disassembly = open('temp_disassemble', 'r').read().split()

    # Blacklisted opcodes
    blacklist = [
      'IMPORT_NAME', 
      '(exec)',
      '(eval)',
      '(compile)',
      '(open)',
      '(balance)',
      '(__class__)',
      '(__delattr__)',
      '(__dict__)',
      '(__dir__)',
      '(__doc__)',
      '(__eq__)',
      '(__format__)',
      '(__ge__)',
      '(__getattribute__)',
      '(__gt__)',
      '(__hash__)',
      '(__init__)',
      '(__init_subclass__)',
      '(__le__)',
      '(__lt__)',
      '(__module__)',
      '(__ne__)',
      '(__new__)',
      '(__reduce__)',
      '(__reduce_ex__)',
      '(__repr__)',
      '(__setattr__)',
      '(__sizeof__)',
      '(__str__)',
      '(__subclasshook__)',
      '(__weakref__)',
      '(calc_gas)',
      '(charge_gas)',
      '(deposit)',
      '(exec_contract)',
      '(generateFunctions)',
      '(get_address)',
      '(get_balance)',
      '(get_body)',
      '(get_contract_code)',
      '(get_state)',
      '(is_contract)',
      '(is_contract_clean)',
      '(make_account)',
      '(modify_state)',
      '(set_address)',
      '(set_balance)',
      '(set_contract_code)',
      '(set_state)',
      '(withdraw)',
      '(balance)',
      '(contract_code)',
      '(contract_hash)',
      '(funcs)',
      '(funcs_args)'
      ]

    # Return false if there are any blacklisted opcodes
    if any(check in disassembly for check in blacklist):
      return False

    return True
  
  def generateFunctions(self, contract_code: str) -> bool:
    co_contract_code = compile(contract_code, 'temp_compile', 'exec')
    # Extracts the functions by checking their type after compilation
    # functions will have code object type instead of a string
    # Initializes the contract with the functions
    injected_context = {
        'state': {},
        'data': {}
    }
    exec(co_contract_code, injected_context)

    # The functions themselves can be extracted from the injected_context
    _extracted_funcs = [constant for constant in co_contract_code.co_consts if type(constant) == type(compile('', '', 'exec'))]
    self.funcs = {str(func.co_name): injected_context[str(func.co_name)] for func in _extracted_funcs}
    # Generates the arguments
    self.funcs_args = {func_name: func.__code__.co_varnames for (func_name,func) in self.funcs.items()}

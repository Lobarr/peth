import base64
from contextlib import redirect_stdout
from copy import deepcopy
from dis import dis
from io import StringIO

from .helper import Helper, GAS_PRICE
from .transaction import Transaction

DEFAULT_BALANCE = 10.0

# Blacklisted opcodes
BLACKLISTS = [
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
  '(generate_functions)',
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

class Account:

  def __init__(self, address: str = '', balance: float = DEFAULT_BALANCE, contract_code: str = "", contract_hash: str = None, state: dict = {}):
    self.address: str = address if address else Helper.generate_address()
    self.balance: float = balance
    self.contract_code = contract_code

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
    code = base64.urlsafe_b64decode(contract_code).decode('utf-8')
    security_clearance = self.is_contract_clean(code)
    if not security_clearance:
      return False

    self.contract_code = code
    self.contract_hash = Helper.hash_data(self.get_contract_code().encode('utf-8'))
    self.generate_functions(self.contract_code)

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
      gas_cost = float(num_of_instructions) * GAS_PRICE
      return float(gas_cost)

    return 0

  def exec_contract(self, transaction: Transaction) -> bool:
    try:
      func_name = transaction.get_data()['func_name']
      func_args = tuple(transaction.get_data()['func_args'])
      if (
        type(func_name) is str
        and type(func_args) is tuple
        and func_name in self.funcs
        and self.calc_gas(func_name) < transaction.get_gas_limit()
      ):
        self.funcs[func_name](*func_args)
        return True
      return False
    except:
      return False

  def modify_state(self, modified_state: dict):
    self.state.update(modified_state)

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
    if any(check in disassembly for check in BLACKLISTS):
      return False
    return True
  
  def generate_functions(self, contract_code: str) -> bool:
    co_contract_code = compile(contract_code, 'temp_compile', 'exec')
    # Extracts the functions by checking their type after compilation
    # functions will have code object type instead of a string
    # Initializes the contract with the functions
    injected_context = {
        'state': {},
        'data': {},
        'msg': {
          'sender': self.get_address(),
	      }
    }
    exec(co_contract_code, injected_context)

    # Set the initial state
    self.set_state(injected_context['state'])

    # The functions themselves can be extracted from the injected_context
    _extracted_funcs = [constant for constant in co_contract_code.co_consts if type(constant) == type(compile('', '', 'exec'))]
    self.funcs = {str(func.co_name): injected_context[str(func.co_name)] for func in _extracted_funcs}
    # Generates the arguments
    self.funcs_args = {func_name: func.__code__.co_varnames for (func_name,func) in self.funcs.items()}

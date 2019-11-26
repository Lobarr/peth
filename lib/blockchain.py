import time
import binascii
import os
from typing import List, Dict
from random import randrange
from mpt import MerklePatriciaTrie
from lib.wallet import Wallet
from lib.transaction import Transaction
from lib.helper import Helper
from lib.account import Account
from lib.crypto import Crypto

# constants
BLOCK_SIZE = 10
NONCE_SIZE = 8

class Blockchain:
  DEFAULT_TARGET: int = 4
  GAS_PRICE: int = 5
  def __init__(self):
      self.chain: List[dict] = []
      self.difficulty_target: int = Blockchain.DEFAULT_TARGET
      self.wallets: Dict[str, Wallet] = {}
      self.accounts: Dict[str, Account] = {}
      self.mempool: Dict[str, Transaction] = {}
      self.mine_block() # genesis block

  def create_wallet(self, address: str) -> dict:
      # define wallet with fields: public_key, private_key, balance
      # add new wallet to self.wallets 
      # return the wallet to caller
      account = self.get_account(address)
      if account == None:
        raise Exception('account does not exist')

      if self.get_wallet_by_address(address) != None:
        raise Exception('account has owner')
      
      new_wallet = Wallet(address=address)
      self.wallets[new_wallet.get_address()] = new_wallet
      return new_wallet.get_data()

  def create_account(self, code: str = None):
    account = Account()
    code != None and account.set_contract_code(code)
    self.accounts[account.get_address()] = account
    return account.get_body()
 
  def get_wallet_by_private_key(self, private_key: str) -> Wallet:
    for wallet_address in self.wallets.keys():
      wallet = self.wallets[wallet_address]
      if wallet.get_private_key() == private_key:
        return wallet
    return None

  def get_wallet_by_public_key(self, public_key: str) -> Wallet:
    for wallet_address in self.wallets.keys():
      wallet = self.wallets[wallet_address]
      if wallet.get_public_key() == public_key:
        return wallet
    return None
      
  def get_wallet_by_address(self, address: str) -> Wallet:
    if address in self.wallets:
      return self.wallets[address]
    return None

  def get_account_last_state(self, address: str) -> dict:
    for i in range(len(self.chain)-1, 0, -1):
      block = self.chain[i]
      states = block['states']
      storage = {}
      patricia_tree = MerklePatriciaTrie(storage, bytes.fromhex(states))
      try:
        account_data_bytes = patricia_tree.get(address.encode('utf-8'))
        account_data = Helper.bytes_to_object(account_data_bytes)
        account = Account.make_account(account_data)
        return account.get_state()
      except KeyError:
        continue
    return None

  def get_account_last_transaction(self, address: str) -> Transaction:
    for i in range(len(self.chain)-1, 0, -1):
      block = self.chain[i]
      transactions = block['transactions']
      for _, transaction_data in transactions:
        transaction = Transaction.make_transaction(transaction_data)
        if transaction.get_sender() == address:
          return transaction
    return None

  def add_transaction_to_mempool(self, transaction_id: str, transaction: Transaction) -> bool:
      #!! validate transaction
      sender_wallet = self.get_wallet_by_address(transaction.get_sender())
      sender_prev_transaction = self.get_account_last_transaction(transaction.get_sender())
      if (
        transaction.hash_transaction() != transaction_id 
        or transaction_id in self.mempool
        or sender_wallet == None
        or transaction.verify_signature(sender_wallet.get_public_key()) == False 
        or (sender_prev_transaction and sender_prev_transaction.get_nonce() >= transaction.get_nonce())
      ):
        return False
      self.mempool[transaction_id] = transaction
      return True
  
  def verify_transaction_sender(self, private_key: str, transaction: Transaction) -> bool:
    wallet = self.get_wallet_by_private_key(private_key)
    if (
      not wallet
      or wallet.get_address() != transaction.get_sender()
    ):
      return False
    return True

  def update_wallets(self, *wallets):
    for wallet in wallets:
      self.wallets[wallet.get_public_key()] = wallet


  def get_transaction_wallets(self, transaction: Transaction) -> tuple:
    sender_account = self.wallets[transaction.get_from_address()]
    recipient_account = self.wallets[transaction.get_to_address()]
    return (sender_account, recipient_account)

  def get_transaction_accounts(self, transaction: Transaction):
    sender_account = self.accounts[transaction.get_sender()]
    recipient_account = self.accounts[transaction.get_recipient()]
    return (sender_account, recipient_account)

  def choose_random_transaction(self, bucket: list):
    return bucket[randrange(0, len(bucket))]


  def get_mempool_as_list(self):
    return [self.mempool[transaction_key].get_data() for transaction_key in self.mempool.keys()]


  def choose_transactions_from_mempool(self) -> List[Transaction]:
    chosen_transactions = []
    transaction_bucket = [self.mempool[transaction_id] for transaction_id in self.mempool.keys()]

    while len(chosen_transactions) != BLOCK_SIZE:
      if not transaction_bucket:
        break

      chosen_transaction = self.choose_random_transaction(transaction_bucket)
      sender_account, recipient_account = self.get_transaction_accounts(chosen_transaction)
      if recipient_account.is_contract():
        gas = recipient_account.calc_gas()
        sender_account.charge_gas(gas) and recipient_account.exec_contract(chosen_transaction)
      else:
        #! handle either sending data / sending funds
        if sender_account.withdraw(chosen_transaction.get_amount()): # attempt to spend
          recipient_account.deposit(chosen_transaction.get_amount())
          self.update_wallets(sender_account, recipient_account)
          chosen_transactions.append(chosen_transaction)
      
      del self.mempool[chosen_transaction.get_hash()]
      transaction_bucket.remove(chosen_transaction)
    
    return chosen_transactions

  def get_accounts(self) -> Dict[str, Account]:
    return self.accounts

  def calculate_state_root(self):
    # make merkle patricia tree of accounts
    state_storage = {}
    state_tree = MerklePatriciaTrie(state_storage)
    
    for account_address, account in self.get_accounts():
      state_tree.update(account_address.encode('utf-8'), Helper.object_to_bytes(account.get_body()))

  def hash_transactions(self, first_transaction: Transaction, second_transaction: Transaction):
    combined_hash = first_transaction.get_hash().encode('utf-8') + second_transaction.get_hash().encode('utf-8')
    return Helper.hash_data(combined_hash)


  def calculate_transactions_root(self, transactions: list):
      # calculate the merkle root
      # return the merkle root (hash)
      cur_tree_level = transactions # starts at bottom of the tree (leaf nodes - transactions)
      if cur_tree_level:
        while len(cur_tree_level) != 1: 
          # loops till there's only the root node left
          next_level = []
          if len(cur_tree_level) % 2 != 0:
            # balances odd numbeered nodes
            cur_tree_level.append(cur_tree_level[-1])
          
          for i in range(0, len(cur_tree_level), 2):
            first_transaction = cur_tree_level[i]
            second_transaction = cur_tree_level[i+1]
            combined_transaction = Transaction()
            combined_transaction.set_hash(self.hash_transactions(first_transaction, second_transaction))
            next_level.append(combined_transaction)
          
          cur_tree_level = next_level
        return cur_tree_level[0].get_hash() # merkle root hash
      return None


  def check_transactions_root(self, block: dict):
    # check merkle root
    # return OK or BAD
    transactions = []
    for transaction_id in block['transactions'].keys():
      transaction_data = block['transactions'][transaction_id]
      transaction = Transaction.make_transaction(transaction_data)
      transactions.append(transaction)

    return True if self.calculate_transactions_root(transactions) == block['header']['transactions_root'] else False


  def create_block(self, data = None):
      block = {
          'hash' : None,
          'header' : {
              'nonce': None,
              'number': len(self.chain),
              'timestamp': str(time.time()),
              'difficulty': self.difficulty_target,
              'gas_limit': None,
              'gas_used': None,
              'parent_hash': self.get_last_block_hash(),
              'states_root_hash': None,
              'transactions_root_hash': None,
          },
          'states': None,
          'transactions': None,
      }
      return block

  def mine_block(self, data = None):
      block = self.create_block(data)
      transactions = self.choose_transactions_from_mempool()
      
      if transactions:
        for transaction in transactions:
          block['transactions'][transaction.hash_transaction()] = transaction.get_body()
        block['header']['transactions_root_hash'] = self.calculate_transactions_root()

      if self.get_accounts():
        states_root, states_root_hash = self.get_patricia_root(self.get_accounts())
        block['states'] = states_root
        block['states']['states_root_hash'] = states_root_hash

      while True:
          block['header']['nonce'] = binascii.b2a_hex(os.urandom(NONCE_SIZE)).decode('utf-8')
          block['hash'] = self.hash_block_header(block)

          if block['hash'][:self.difficulty_target] == ('0' * self.difficulty_target):
              break

      self.chain.append(block)
      return block

  def get_patricia_root(self, accounts: List[Account]) -> tuple:
    storage = {}
    patricia_tree = MerklePatriciaTrie(storage)
    for account in accounts:
      address_bytes = account.get_address().encode('utf-8')
      account_body_bytes = Helper.object_to_bytes(account.get_body())
      patricia_tree.update(address_bytes, account_body_bytes) 
    tree_root = patricia_tree.root().hex()
    tree_root_hash = patricia_tree.root_hash().hex()
    return (tree_root, tree_root_hash)
  
  def get_last_block_hash(self):
      return self.chain[-1]['hash'] if self.chain else None

  def hash_block_header(self, block):
      block_header_bytes = Helper.object_to_bytes(block['header'])
      return Helper.hash_data(block_header_bytes)

  def get_account(self, address: str) -> Account:
    if address not in self.accounts:
      return None
    return self.accounts[address]

  def check(self):
      for number in reversed(range(len(self.chain))):
        block = self.chain[number]
        if (
          (number > 0 and block['header']['parent_hash'] != self.chain[number-1]['hash'])
          or block['hash'] != self.hash_block_header(block)
          or self.check_transactions_root(block) == False
        ):
          False
      return True

  def get_wallet_summaries(self): 
    summaries = []
    for wallet_address in self.wallets.keys():
      wallet = self.get_wallet_by_address(wallet_address)
      associated_account = self.get_account(wallet.get_address())
      wallet_summary = wallet.get_summary(associated_account)
      summaries.append(wallet_summary)
    return summaries

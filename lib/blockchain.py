import time
import binascii
import os

from typing import List, Dict
from random import randrange
from . import Wallet, Transaction, Helper, Account

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
      if account != None:
        raise Exception('Account has owner')
      new_wallet = Wallet(address=address)
      self.wallets[new_wallet.get_public_key()] = new_wallet
      return new_wallet.get_data()

  def get_wallet_by_private_key(self, private_key: str) -> Wallet:
    wallets = self.wallets.keys()
    for wallet in wallets:
      if wallets[wallet].get_private_key() == private_key:
        return wallet
    return None

  def get_wallet_by_public_key(self, public_key: str) -> Wallet:
    wallets = self.wallets.keys()
    for wallet in wallets:
      if wallets[wallet].get_public_key() == public_key:
        return wallet
      
  def get_wallet_by_address(self, address: str) -> wallet:
    if address in self.wallets:
      return self.wallets[address]
    return None

  def get_account_by_address(self, address: str) -> Account:
    if address in self.accounts:
      return self.accounts[address]
    return None

  def get_account_last_state(self, address: str) -> dict:
    if address not in self.accounts:
      raise Exception('account does not exist')
    account = self.accounts[address]
    return account.get_state()

  def hash_transaction(self, transaction: Transaction) -> str:
      # hash transaction
      # return hash
      return transaction.hash_transaction()

  def add_transaction_to_mempool(self, transaction_id: str, transaction: Transaction) -> bool:
      # validate transaction
      # add transaction to self.mempool
      # return OK or BAD
      if (
        transaction.hash_transaction() != transaction_id 
        or transaction_id in self.mempool
      ):
        return False
      self.mempool[transaction_id] = transaction
      return True
  

  def update_wallets(self, *wallets):
    for wallet in wallets:
      self.wallets[wallet.get_public_key()] = wallet


  def get_transaction_wallets(self, transaction: Transaction) -> tuple:
    from_wallet = self.wallets[transaction.get_from_address()]
    to_wallet = self.wallets[transaction.get_to_address()]
    return (from_wallet, to_wallet)


  def choose_random_transaction(self, bucket: list):
    return bucket[randrange(0, len(bucket))]


  def get_mempool_as_list(self):
    return [self.mempool[transaction_key].get_data() for transaction_key in self.mempool.keys()]


  def choose_transactions_from_mempool(self):
    # choose 10 random transactions
        # check if the balances allow spending the amount
        # change the balance for the sender
        # change the balance for the recipient
        # remove transaction from mempool
    # return transactions to caller
    chosen_transactions = []
    transaction_bucket = [self.mempool[transaction_id] for transaction_id in self.mempool.keys()]

    while len(chosen_transactions) != BLOCK_SIZE:
      if not transaction_bucket:
        break
      
      chosen_transaction = self.choose_random_transaction(transaction_bucket)
      from_wallet, to_wallet = self.get_transaction_wallets(chosen_transaction)
      #TODO: handle contract / external transction
      if from_wallet.withdraw(chosen_transaction.get_amount()): # attempt to spend
        to_wallet.deposit(chosen_transaction.get_amount())
        self.update_wallets(from_wallet, to_wallet)
        chosen_transactions.append(chosen_transaction)
      
      del self.mempool[chosen_transaction.get_hash()]
      transaction_bucket.remove(chosen_transaction)
    
    return chosen_transactions

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
              'receipts_root': None,
              'states_root': None,
              'transactions_root': None,
              'receipts_root': None
          },
          'states': {},
          'transactions': {},
          'receipts': {}
      }
      return block


  def mine_block(self, data = None):
      block = self.create_block(data)
      transactions = self.choose_transactions_from_mempool()

      for transaction in transactions:
        block['transactions'][transaction.get_hash()] = transaction.get_data()

      block['header']['transactions_root'] = self.calculate_transactions_root(transactions)

      while True:
          block['header']['nonce'] = binascii.b2a_hex(os.urandom(NONCE_SIZE)).decode('utf-8')
          block['hash'] = self.hash_block_header(block)

          if block['hash'][:self.difficulty_target] == ('0' * self.difficulty_target):
              break

      self.chain.append(block)
      return block


  def get_last_block_hash(self):
      return self.chain[-1]['hash'] if self.chain else None


  def hash_block_header(self, block):
      block_header_bytes = repr(block['header']).encode('utf-8')
      return Helper.hash_data(block_header_bytes)


  def verify_transaction_sender(self, sender_private_key: str, transaction: Transaction):
    return sender_private_key == self.wallets[transaction.get_from_address()].get_private_key()

  def get_account(self, address: str) -> Account:
    if address not in self.accounts:
      return None
    return self.accounts[address]

  def check(self):
      for number in reversed(range(len(self.chain))):
          block = self.chain[number]

          if not block['hash'] == self.hash_block_header(block):
              return 'invalid block hash for block ' + str(number)

          if (
            number > 0 and 
            block['header']['parent_hash'] != self.chain[number - 1]['hash']
          ):
              return 'invalid block pointer from block ' + str(number) + ' back to block ' + str(number - 1)

          if not self.check_transactions_root(block):
              return 'invalid merkle root for block ' + str(number)##
      return True

  def get_wallet_summaries(self): 
    return [self.wallets[wallet_key].get_summary() for wallet_key in self.wallets.keys()]

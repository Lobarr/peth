import json
from random import randrange
from flask import Flask, jsonify, request, json, Response
from lib import Blockchain, Transaction, Crypto, Helper
from mpt import MerklePatriciaTrie

app = Flask(__name__)

"""
@api {get} /create_wallet Create wallet on the blockchain
@apiName CreateWallet
@apiGroup Blockchain

@apiParamExample {json} Request-Example:
  {
    "address": "some-address"
  }

@apiSuccessExample {json} Success-Response:
  HTTP/1.1 200 OK
  {
    "data": {
      "address": "some-address",
      "private_key": "some-private-key",
      "public_key": "some-public-key"
    }
  }

@apiErrorExample {json} Error-Response:
  HTTP/1.1 400 Bad Request
  {
    "error": "some-error"
  }
"""
@app.route('/create_wallet', methods=['GET'])
def create_wallet():
  try:
    address = request.args.get('address', type=str)
    if not address:
      return jsonify({
        'error': 'address not provided'
      }), 400
    return jsonify({
      'data': blockchain.create_wallet(address)
    }), 200
  except Exception as err:
    return jsonify({'error': err.args[0]})

"""
@api {get} /create_account Create account on the blockchain
@apiName CreateAccount
@apiGroup Blockchain

@apiParamExample {json} Request-Example:
  {
    "code": "some-encoded-contract-code"
  }

@apiSuccessExample {json} Response-Example:
  HTTP/1.1 200 OK
  {
    "address": "some-address",
    "balance": 10.0,
    "contract_code": "some-contract-code",
    "contract_hash": "some-contract-hash",
    'funcs': [],
    'funcs_args': {},
    'state': {}
  }
"""
@app.route('/create_account', methods=['GET'])
def create_account():
  return jsonify({
    'data': blockchain.create_account(request.args.get('code', type=str))
  }), 200

@app.route('/show_mempool', methods = ['GET'])
def show_mempool():
  return jsonify({
    'data': blockchain.get_mempool_as_list()
  }), 200


"""
@api {get} /create_transaction Create transaction on the blockchain
@apiName CreateAccount
@apiGroup Blockchain

@apiParamExample {json} Request-Example:
  {
    "amount": 0,
    "data": "some-json-encoded-data",
    "gas_limit": 1.0,
    "sender": "some-address",
    "recipient": "some-address",
    "private_key": "some-private-key"
  }

@apiSuccessExample {json} Response-Example:
  {
    "transaction_hash": "some-trasnaction-hash"
  }

@apiErrorExample {json} Error-Response:
  HTTP/1.1 400 Bad Request
  {
    "error": "some-error"
  }
"""
@app.route('/create_transaction', methods = ['GET'])
def create_transaction():
  try:
    transaction_data = {
      'amount': request.args.get('amount', type=float),
      'data': request.args.get('data', default=None),
      'gas_limit': request.args.get('gas_limit', type=float),
      'sender': request.args.get('sender', type=str),
      'recipient': request.args.get('recipient', type=str),
      'private_key': request.args.get('private_key', type=str)
    }
    # Check the data field for correct function name and parameters
    data = json.loads(transaction_data['data'])
    if transaction_data['data'] != None:
      if 'func_name' in data or 'func_args' in data:
        func_name = data['func_name']
        func_args = data['func_args']
        contract_account = blockchain.get_account(transaction_data['recipient'])
        # Perform Checks
        if contract_account.is_contract() == False:
          raise Exception('Recipient is not a contract account')
          
        if func_name not in contract_account.funcs.keys():
          raise Exception('Function call does not exist for the contract')
          
        if len(func_args) != len(contract_account.funcs_args[func_name]):
          raise Exception('Wrong amount of function arugments')

    transaction = blockchain.create_transaction(transaction_data)
    return jsonify({'data': {'transaction_hash': transaction.get_hash()}}), 200
  except Exception as err:
    return jsonify({'error': err.args[0]}), 400

"""
@api {get} /mine_block Mines block with transactions from mempool
@apiName MineBlock
@apiGroup Blockchain

@apiParamExample {json} Request-Example:
  {
    "data": "some-data"
  }

@apiSuccessExample {json} Response-Example:
  HTTP/1.1 200 OK
  {
    "result": {
      "hash": "some-hash",
      "header": {
        "difficulty": 4,
        "gas_limit": null,
        "gas_used": null,
        "nonce": "some-nonce",
        "number": 1,
        "parent_hash": "some-hash",
        "states_root_hash": "some-hash",
        "timestamp": "some-timestamp",
        "transactions_root_hash": "some-hash"
      },
      "states": "some-patricia-root",
      "transactions": {
        "some-hash": {
          "amount": 2.0,
          "data": null,
          "gas_limit": 1.0,
          "gas_price": null,
          "hash": "some-hash",
          "nonce": 0,
          "recipient": "some-address",
          "sender": "some-address",
          "signature": "some-signature"
        }
      }
    }
  }
"""
@app.route('/mine_block', methods = ['GET'])
def mine_block():
  block_data = request.args.get('data', default=None, type=str)
  return jsonify({'result': blockchain.mine_block(block_data)}), 200

"""
@api {get} /check_blockchain Verifies integrity of blockchain 
@apiName CheckBlockchain
@apiGroup Blockchain

@apiSuccessExample {json} Response-Example:
  HTTP/1.1 200 OK
  {
    "result": true
  }
"""
@app.route('/check_blockchain', methods = ['GET'])
def check_blockchain():
  return jsonify({'result': blockchain.check()}), 200


"""
@api {get} /get_blocks Gets blocks in the blockchain 
@apiName GetBlocks
@apiGroup Blockchain

@apiSuccessExample {json} Response-Example:
  HTTP/1.1 200 OK
  {
    "result": [
      {
        "hash": "some-hash",
        "header": {
          "difficulty": 4,
          "gas_limit": null,
          "gas_used": null,
          "nonce": "some-nonce",
          "number": 0,
          "parent_hash": null,
          "states_root_hash": null,
          "timestamp": "some-timestampe",
          "transactions_root_hash": null
        },
        "states": null,
        "transactions": {}
      }
    ]
  }
"""
@app.route('/get_blocks', methods = ['GET'])
def get_blocks():
  return jsonify({'result': blockchain.chain}), 200

"""
@api {get} /get_block Gets block in the blockchain 
@apiName GetBlocks
@apiGroup Blockchain

@apiParamExample {json} Request-Example:
  {
    "height": 0
  }

@apiSuccessExample {json} Response-Example:
  HTTP/1.1 200 OK
  {
    "result": {
      "hash": "some-hash",
      "header": {
        "difficulty": 4,
        "gas_limit": null,
        "gas_used": null,
        "nonce": "some-nonce",
        "number": 0,
        "parent_hash": null,
        "states_root_hash": null,
        "timestamp": "some-timestampe",
        "transactions_root_hash": null
      },
      "states": null,
      "transactions": {}
    }
  }

@apiErrorExample {json} Error-Example:
  HTTP/1.1 400 Bad Request
  {
    "error": "some-error"
  }
"""
@app.route('/get_block', methods = ['GET'])
def get_block():
  try:
    block_number = request.args.get('height', default=0, type=int)
    return jsonify({'result': blockchain.chain[block_number]}), 200
  except IndexError:
    return jsonify({'error': 'invald block number'}), 400

"""
@api {get} /get_account Gets account in the blockchain 
@apiName GetAccount
@apiGroup Blockchain

@apiParamExample {json} Request-Example:
  {
    "address": "some-address"
  }

@apiSuccessExample {json} Response-Example:
  HTTP/1.1 200 OK
  {
    "data": {
      "address": "some_address",
      "balance": 10.0,
      "contract_code": "some-code",
      "contract_hash": "some-hash",
      "state": {
        "counter": 1,
        "initialized": true,
        "msg": {
          "nonce": 0,
          "sender": "some-address"
        }
      }
    }
  }

@apiErrorExample {json} Error-Example:
  HTTP/1.1 400 Bad Request
  {
    "error": "some-error"
  }
"""
@app.route('/get_account', methods = ['GET'])
def get_account():
  account_address = request.args.get('address', type=str)
  account = blockchain.get_account(account_address)
  if account == None:
    return jsonify({'error': 'Invalid address provided'})
  return jsonify({'data': account.get_body()})

"""
@api {get} /get_accounts Gets accounts in the blockchain 
@apiName GetAccounts
@apiGroup Blockchain

@apiSuccessExample {json} Response-Example:
  HTTP/1.1 200 OK
  {
    "data": {
      "df513a89f6e63dd993514a32e1847f54": {
        "address": "df513a89f6e63dd993514a32e1847f54",
        "balance": 10.0,
        "contract_code": "some-contract",
        "contract_hash": "some-hash",
        "funcs": [
          "addStudent",
          "removeStudent",
          "setTeacher",
          "setMaxSize",
          "setSubject",
          "getStudents",
          "getTeacher",
          "getMaxSize",
          "getCurrentSize",
          "getSubject"
        ],
        "funcs_args": {
          "addStudent": [
            "name"
          ],
          "getCurrentSize": [],
          "getMaxSize": [],
          "getStudents": [],
          "getSubject": [],
          "getTeacher": [],
          "removeStudent": [
            "name"
          ],
          "setMaxSize": [
            "new_max_size"
          ],
          "setSubject": [
            "subject"
          ],
          "setTeacher": [
            "teacher"
          ]
        },
        "state": {
          "admin": "df513a89f6e63dd993514a32e1847f54",
          "current_size": 0,
          "max_size": 30,
          "students": [],
          "subject": "",
          "teacher": ""
        }
      },
      "ecb5238175b53317f599b4e42ae87e9a": {
        "address": "ecb5238175b53317f599b4e42ae87e9a",
        "balance": 10.0,
        "contract_code": "",
        "contract_hash": null,
        "funcs": [],
        "funcs_args": {},
        "state": {}
      }
    }
  }

@apiErrorExample {json} Error-Example:
  HTTP/1.1 400 Bad Request
  {
    "error": "some-error"
  }
"""
@app.route('/get_accounts', methods = ['GET'])
def get_accounts():
  if blockchain.get_accounts() == None:
    return jsonify({'error': 'No accounts available'})

  accounts = {address: account.get_body() for address, account in blockchain.get_accounts().items()}
  return jsonify({'data': accounts})  

"""
@api {get} /show_balances Gets summary of wallets in the blockchain 
@apiName GetAccounts
@apiGroup Blockchain

@apiSuccessExample {json} Response-Example:
  HTTP/1.1 200 OK
  {
    "data": [
      {
        "address": "some-address",
        "balance": 0
        "public_key": "some-public-key",
      }
    ]
  }
"""
@app.route('/show_balances', methods = ["GET"])
def show_balances():
  return jsonify({
    'data': blockchain.get_wallet_summaries()
  }), 200


blockchain = Blockchain()
if __name__ == '__main__':
  app.run(host = '0.0.0.0', port = 8080, debug=1)


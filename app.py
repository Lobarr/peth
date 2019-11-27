'''
Jesuloba Egunjobi (100613629)
Nicolas Bermeo (100625305)
'''

import json
from random import randrange
from flask import Flask, jsonify, request, json, Response
from lib import Blockchain, Transaction, Crypto, Helper
from mpt import MerklePatriciaTrie

app = Flask(__name__)

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
    transaction = blockchain.create_transaction(transaction_data)
    return jsonify({'data': transaction.get_hash()}), 200
  except Exception as err:
    return jsonify({'error': err.args[0]}), 400

@app.route('/mine_block', methods = ['GET'])
def mine_block():
  block_data = request.args.get('data', default=None, type=str)
  return jsonify({'result': blockchain.mine_block(block_data)}), 200


@app.route('/check_blockchain', methods = ['GET'])
def check_blockchain():
  return jsonify({'result': blockchain.check()}), 200


@app.route('/get_blocks', methods = ['GET'])
def get_blocks():
  return jsonify({'result': blockchain.chain}), 200


@app.route('/get_block', methods = ['GET'])
def get_block():
  try:
    block_number = request.args.get('height', default=0, type=int)
    return jsonify({'result': blockchain.chain[block_number]}), 200
  except IndexError:
    return jsonify({'error': 'invald block number'}), 400

@app.route('/get_account', methods = ['GET'])
def get_account():
  account_address = request.args.get('address', type=str)
  account = blockchain.get_account(account_address)
  if account == None:
    return jsonify({'error': 'Invalid address provided'})
  return jsonify({'data': account.get_body()})

@app.route('/show_balances', methods = ["GET"])
def show_balances():
  return jsonify({
    'data': blockchain.get_wallet_summaries()
  }), 200


blockchain = Blockchain()
if __name__ == '__main__':
  app.run(host = '0.0.0.0', port = 8080, debug=1)


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
  transaction = Transaction()
  transaction.set_amount(request.args.get('amount', type=float))
  data = request.args.get('data') # any json data

  if data != None:
    transaction.set_data(json.loads(data))

  transaction.set_gas_limit(request.args.get('gas_limit', type=float))
  transaction.set_sender(request.args.get('sender', type=str))
  sender_prev_transaction = blockchain.get_account_last_transaction(transaction.get_sender())
  
  if sender_prev_transaction:
    transaction.set_nonce(sender_prev_transaction.get_nonce()+1)

  transaction.set_recipient(request.args.get('recipient', type=str))
  sender_private_key = request.args.get('private_key', type=str)
  signature = Crypto.sign(transaction.get_body(), sender_private_key)
  transaction.set_signature(signature)

  transaction_hash = transaction.hash_transaction()

  if (
    not blockchain.verify_transaction_sender(sender_private_key, transaction)
    or not blockchain.add_transaction_to_mempool(transaction_hash, transaction)
  ):
      return jsonify({'error': 'Invalid transaction'}), 400

  return jsonify({'transaction_hash': transaction_hash}), 200


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
    block_number = request.args.get('number', default=0, type=int)
    return jsonify({'result': blockchain.chain[block_number]}), 200
  except IndexError:
    return jsonify({'error': 'invald block number'}), 400


@app.route('/show_balances', methods = ["GET"])
def show_balances():
  return jsonify({
    'data': blockchain.get_wallet_summaries()
  }), 200


blockchain = Blockchain()
app.run(host = '0.0.0.0', port = 8080, debug=1)


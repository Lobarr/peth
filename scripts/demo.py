import base64
import json
import os
import requests

def encode_contract(contract_path: str) -> str:
  with open(contract_path, 'rb') as file:
    contract = file.read()
    return base64.urlsafe_b64encode(contract).decode('utf-8')
  return ''

api = 'http://localhost:5000'

sender_account = requests.get(f'{api}/create_account').json()['data']
sender_wallet = requests.get(f"{api}/create_wallet?address={sender_account['address']}").json()['data']

contract_path = os.path.abspath('./contract/sample.py')
encoded_contract_code = encode_contract(contract_path)
contract_account = requests.get(f"{api}/create_account?code={encoded_contract_code}").json()['data']
contract_wallet = requests.get(f"{api}/create_wallet?address={contract_account['address']}").json()['data']

transaction_data = {
  'amount': 5.0,
  'data': json.dumps({'func_name': 'addStudent', 'func_args': ('bob',)}),
  'gas_limit': 2.0,
  'sender': sender_account['address'],
  'recipient': contract_account['address'],
  'private_key': sender_wallet['private_key']
}

transaction_hash = requests.get(f"{api}/create_transaction?amount={transaction_data['amount']}&data={transaction_data['data']}&gas_limit={transaction_data['gas_limit']}&sender={transaction_data['sender']}&recipient={transaction_data['recipient']}&private_key={transaction_data['private_key']}").json()['data']

print('sender account\n', sender_account, '\n')
print('sender wallet\n', sender_wallet, '\n')
print('encoded contract code\n', encoded_contract_code, '\n')
print('contract account\n', contract_account, '\n')
print('contract wallet\n', contract_wallet, '\n')
print('transaction hash\n', transaction_hash, '\n')

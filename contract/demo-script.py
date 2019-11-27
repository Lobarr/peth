import requests
import json

account_1 = requests.get('http://localhost:8080/create_account')
url = str(f"http://localhost:8080/create_wallet?address={account_1.json()['data']['address']}")
wallet_1 = requests.get(url)

account_2 = requests.get("http://localhost:8080/create_account?code=%27IyBEZWNsYXJlIHRoZSBzdGF0ZSB2YXJpYWJsZXMKIyB3aWxsIG9ubHkgaGFwcGVuIG9uY2UgZHVyaW5nIGNvbnRyYWN0IGNyZWF0aW9uCnN0YXRlWyJzdHVkZW50cyJdOiBsaXN0ID0gW10gaWYgInN0dWRlbnRzIiBub3QgaW4gc3RhdGUgZWxzZSBzdGF0ZVsic3R1ZGVudHMiXQpzdGF0ZVsidGVhY2hlciJdOiBzdHIgPSAiIiBpZiAidGVhY2hlciIgbm90IGluIHN0YXRlIGVsc2Ugc3RhdGVbInRlYWNoZXIiXQpzdGF0ZVsibWF4X3NpemUiXTogaW50ID0gMzAgaWYgIm1heF9zaXplIiBub3QgaW4gc3RhdGUgZWxzZSBzdGF0ZVsibWF4X3NpemUiXQpzdGF0ZVsiY3VycmVudF9zaXplIl06IGludCA9IDAgaWYgImN1cnJlbnRfc2l6ZSIgbm90IGluIHN0YXRlIGVsc2Ugc3RhdGVbImN1cnJlbnRfc2l6ZSJdCnN0YXRlWyJzdWJqZWN0Il0gPSAiIiBpZiAic3ViamVjdCIgbm90IGluIHN0YXRlIGVsc2Ugc3RhdGVbInN1YmplY3QiXQoKZGVmIGFkZFN0dWRlbnQobmFtZTogc3RyKSAtPiBib29sOgogICMgQWRkIHN0dWRlbnQgb25seSBpZiBjbGFzcyBzaXplIG5vdCBmdWxsCiAgaWYgc3RhdGVbImN1cnJlbnRfc2l6ZSJdIDwgc3RhdGVbIm1heF9zaXplIl06CiAgICBzdGF0ZVsic3R1ZGVudHMiXS5hcHBlbmQobmFtZSkKICAgIHN0YXRlWyJjdXJyZW50X3NpemUiXSArPSAxCiAgICAKICAgIHJldHVybiBUcnVlCiAgcmV0dXJuIEZhbHNlCgpkZWYgcmVtb3ZlU3R1ZGVudChuYW1lOnN0cikgLT4gYm9vbDoKICBpZiBkYXRhWyJuYW1lIl0gaW4gc3RhdGVbInN0dWRlbnRzIl06CiAgICBzdGF0ZVsic3R1ZGVudHMiXS5yZW1vdmUobmFtZSkKICAgIHJldHVybiBUcnVlCiAgCiAgcmV0dXJuIEZhbHNlCgpkZWYgc2V0VGVhY2hlcih0ZWFjaGVyOiBzdHIpIC0-IGJvb2w6CiAgdHJ5OgogICAgc3RhdGVbInRlYWNoZXIiXSA9IHRlYWNoZXIKICAgIHJldHVybiBUcnVlCiAgZXhjZXB0OgogICAgcmV0dXJuIEZhbHNlCiAgCmRlZiBzZXRNYXhTaXplKG5ld19tYXhfc2l6ZTogaW50KSAtPiBib29sOgogIHRyeTogCiAgICBzdGF0ZVsibWF4X3NpemUiXSA9IG5ld19tYXhfc2l6ZQogICAgcmV0dXJuIFRydWUKICBleGNlcHQ6CiAgICByZXR1cm4gRmFsc2UKCmRlZiBzZXRTdWJqZWN0KHN1YmplY3Q6IHN0cikgLT4gYm9vbDoKICB0cnk6CiAgICBzdGF0ZVsic3ViamVjdCJdID0gc3ViamVjdAogICAgcmV0dXJuIFRydWUKICBleGNlcHQ6CiAgICByZXR1cm4gRmFsc2UKCmRlZiBnZXRTdHVkZW50cygpIC0-IGxpc3Q6CiAgcmV0dXJuIHN0YXRlWyJzdHVkZW50cyJdCgpkZWYgZ2V0VGVhY2hlcigpIC0-IHN0cjoKICByZXR1cm4gc3RhdGVbInRlYWNoZXIiXQoKZGVmIGdldE1heFNpemUoKSAtPiBpbnQ6CiAgcmV0dXJuIHN0YXRlWyJtYXhfc2l6ZSJdCgpkZWYgZ2V0Q3VycmVudFNpemUoKSAtPiBpbnQ6CiAgcmV0dXJuIHN0YXRlWyJjdXJyZW50X3NpemUiXQoKZGVmIGdldFN1YmplY3QoKSAtPiBzdHI6CiAgcmV0dXJuIHN0YXRlWyJzdWJqZWN0Il0K%27")
wallet_2 = requests.get(str(f"http://localhost:8080/create_wallet?address={account_2.json()['data']['address']}"))

transaction_data = {
      'amount': 5.0,
      'data': {'func_name': 'addStudent', 'func_args': ('bob',)},
      'gas_limit': 2.0,
      'sender': account_1.json()['data']['address'],
      'recipient': account_2.json()['data']['address'],
      'private_key': wallet_1.json()['data']['private_key']
    }
print(f"&sender={transaction_data['sender']}&recipient={transaction_data['recipient']}")
res = requests.get(str(f"http://localhost:8080/create_transaction?amount={transaction_data['amount']}&data={json.dumps(transaction_data['data'])}&gas_limit={transaction_data['gas_limit']}&sender={transaction_data['sender']}&recipient={transaction_data['recipient']}&private_key={transaction_data['private_key']}"))
print(res.json())

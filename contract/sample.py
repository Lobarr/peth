global state, msg

state['initialized'] = True
if 'counter' in state:
  state['counter'] += 1
else:
  state['counter'] = 1
state['msg'] = msg

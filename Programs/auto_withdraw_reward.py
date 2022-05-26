import os

from Objects.AccountObject import AccountGroup
from Objects.NodeObject import Node

full_node = Node(url=os.getenv("FULL_NODE", "https://mfc88.ddns.net/fn"))
accounts = AccountGroup().load_from_file('./Programs/keys').attach_to_node(full_node)
acc0 = accounts[0]
retry = 3
tx_fee = 10
tx_fee_step = 5
while retry:
    try:
        if acc0.stk_get_reward_amount() > int(200e9):
            tx = acc0.stk_withdraw_reward_to_me(tx_fee=tx_fee).req_to(full_node).get_transaction_by_hash()
            if tx.is_confirmed():
                break
            else:
                tx_fee += tx_fee_step
                retry -= 1
        else:
            print("Too little to care!!!")
            break
    except Exception as e:
        print(e)


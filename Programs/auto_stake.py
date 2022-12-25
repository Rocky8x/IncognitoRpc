from Objects.AccountObject import AccountGroup
from Objects.NodeObject import Node

node = Node("http://....")
accounts = AccountGroup().load_from_file("Programs/key").attach_to_node(node)
funder = accounts[0]
bbsd = node.get_beacon_best_state_detail_info()
for acc in accounts:
    if not bbsd.get_auto_staking_committees(acc):
        for retry in range(5):
            tx = funder.stake_someone_reward_me(acc, auto_re_stake=True)
            if node.get_tx_by_hash(tx.get_tx_id()).is_confirmed():
                break


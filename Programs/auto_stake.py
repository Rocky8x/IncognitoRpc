from Objects.AccountObject import AccountGroup
from Objects.NodeObject import Node

node = Node("https://mfc88.ddns.net/fn")
accounts = AccountGroup().load_from_file("Programs/key").attach_to_node(node)
funder = accounts[0]

unstaked_accounts = accounts.node_monitor_find_unstaked()
for acc in unstaked_accounts:
    tx = funder.stake_someone_reward_me(acc, auto_re_stake=True)
    td = tx.get_transaction_by_hash()



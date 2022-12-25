import os
import time
import traceback

from Configs.Configs import ChainConfig
from Helpers import Logging

ChainConfig.ACCESS_TOKEN = "8449dd297c40e9d188f5b7fa157e636b736cb62641a0c11fbb53d2840386f52c"
from Objects.AccountObject import Account, AccountGroup
from Objects.NodeObject import Node

mfc = Node(url="https://mfc88.ddns.net/fn")
accounts = AccountGroup().load_from_file('./Programs/keys').attach_to_node(mfc)
acc0 = accounts[0]

def find_unstaked():
    bbsd = mfc.get_beacon_best_state_detail_info()
    unstaked = []
    for acc in accounts:
        if bbsd.get_auto_staking_committees(acc) is None:
            unstaked.append(acc)
    return unstaked

def staked_unstaked():
    for acc in find_unstaked():
        tx = acc0.stake_someone_reward_me(acc,auto_re_stake=True)
        td = mfc.get_tx_by_hash(tx.get_tx_id())



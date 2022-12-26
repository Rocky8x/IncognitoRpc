from Configs.Configs import ChainConfig

ChainConfig.ACCESS_TOKEN = "8449dd297c40e9d188f5b7fa157e636b736cb62641a0c11fbb53d2840386f52c"
from Objects.AccountObject import AccountGroup
from Objects.NodeObject import Node

mfc = Node(url="https://mfc88.ddns.net/fn")
accounts = AccountGroup().load_from_file('./Programs/keys').attach_to_node(mfc)
acc0 = accounts[0]

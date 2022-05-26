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
acc0, acc1, acc2, acc3, acc4, acc5, acc6, acc7, acc8 = accounts

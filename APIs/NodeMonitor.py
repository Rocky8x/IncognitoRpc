from APIs import BaseApi
import math
import re
import datetime

from Configs.Configs import ChainConfig


class NodeStatResponseBase:
    def __init__(self, response):
        self.response = response

    @property
    def data(self):
        return self.response.json()


class NodeStat(NodeStatResponseBase):
    ROLES = {
        "Committee": 1,
        "Pending": 2,
        "Unstake": 8
    }

    class Node:
        def __init__(self, stat_data):
            self.stat_data = stat_data
            next_event = self.stat_data["NextEventMsg"]
            reg = re.compile(r'(\d+) epoch to be (\w+)')
            try:
                match = re.match(reg, next_event)
                self.next_event_e_count = int(match.group(1))
                self.next_role = match.group(2)
            except:
                self.next_event_e_count = 0
                self.next_role = ""
                self.next_event_msg = next_event
                self.next_event_time_count = 0
                return
            REMAIN_BLOCK = 0
            self.next_event_time_count = datetime.timedelta(
                seconds=(self.next_event_e_count * 350 + REMAIN_BLOCK) * ChainConfig.BLOCK_TIME)
            msg = "%de (%s) -> %s" % (self.next_event_e_count,
                                      self.next_event_time_count, self.next_role)
            self.next_event_msg = msg.replace(" days", "d").replace(" day", "d")

        @property
        def vote_stat(self):
            return self.stat_data["VoteStat"]

        @property
        def sync_state(self):
            return self.stat_data["SyncState"].capitalize()

        @property
        def committee_shard(self):
            return self.stat_data["CommitteeChain"]

        @property
        def role(self):
            return self.stat_data["CommitteeChain"]

        @property
        def role(self):
            role = self.stat_data.get("Role").capitalize()
            return role if role else "Unstake"

        @property
        def role_code(self):
            return NodeStat.ROLES.get(self.role, 9)

        @property
        def last_vote_stat(self):
            return self.stat_data["LastVoteStat"]

        @property
        def mining_pub_k(self):
            return self.stat_data["MiningPubkey"]

        @property
        def is_slashed(self):
            try:
                return self.stat_data["IsSlashed"]
            except KeyError:
                return False

        @property
        def status(self):
            return self.stat_data["Status"].upper()

        @property
        def auto_stake(self):
            return self.stat_data.get("AutoStake", "")

        @property
        def version(self):
            return self.stat_data.get("Version", "")

        @property
        def is_latest_ver(self):
            return "Old" if self.stat_data["IsOldVersion"] else "Latest"

        @property
        def last_earned_epoch(self):
            regex = re.compile(r'.*\(epoch:(\d+)\)')
            try:
                return int(re.match(regex, self.vote_stat[0]).group(1))
            except IndexError:
                return 0
            except AttributeError:
                return 0

        def short_stat(self):
            return [self.mining_pub_k[-6:], self.status[:3], self.role, self.committee_shard,
                    self.next_event_msg, self.sync_state, self.last_vote_stat, self.is_slashed,
                    self.version, self.is_latest_ver, self.last_earned_epoch]

    def get_unstaked(self):
        unstaked = []
        for node_stat in self.data:
            node = NodeStat.Node(node_stat)
            if node.role == "Unstake":
                unstaked.append(node.mining_pub_k)
        return unstaked


class NodeStatDetail(NodeStatResponseBase):
    @property
    def epoch(self):
        return self.data["Epoch"]

    @property
    def shard(self):
        return self.data["ChainID"]

    @property
    def reward(self):
        r = self.data.get("Reward", 0)
        return r if r is not None else 0

    @property
    def is_slashed(self):
        try:
            return self.data["IsSlashed"]
        except KeyError:
            return False

    @property
    def vote_rate(self):
        total = self.data["totalEpochCountBlock"]
        count = self.data["totalVoteConfirm"]
        try:
            return f"{math.ceil(100*(count/total))}%"
        except ZeroDivisionError:
            return "∞"

    def __str__(self) -> str:
        return 'Epoch %d: shard%d - reward %0.9f - Slashed?%5s - %4s' % (self.epoch, self.shard, self.reward/1e9, self.is_slashed, self.vote_rate)


class NodeMonitorApi(BaseApi):
    URL_BASE = "https://monitor.incognito.org/pubkeystat"

    def __init__(self, url=URL_BASE):
        super().__init__(url)

    def get_nodes_stat(self, keys):
        return NodeStat(self.post("stat", {"mpk": keys}))

    def get_node_detail_stat(self, key):
        return NodeStatDetail(self.post("committee", {"mpk": key}))

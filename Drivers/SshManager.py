import re

from pexpect import pxssh

from Helpers.Logging import config_logger

logger = config_logger(__name__)


class SshManager:
    __SESSIONS = {}

    @staticmethod
    def get_session(host):
        try:
            session = SshManager.__SESSIONS[host]
            logger.debug(f"Use existing ssh connection to {host}")
        except KeyError:
            session = None
            logger.debug(f"No existing ssh connection to {host}")
        return session

    @staticmethod
    def connect(host, username, **auth):
        session = SshManager.get_session(host)
        if not session:
            logger.debug(f"Open new ssh connection to {username}@{host}")
            key = auth.get("key")
            session = pxssh.pxssh.login(host, username, ssh_key=key)
            SshManager.__SESSIONS[host] = session
        return session

    @staticmethod
    def close_all():
        for host, session in SshManager.__SESSIONS.values():
            logger.debug(f"Closing connection to {host}")
            session.close()


class NodeSshAction:
    def __init__(self, session):
        self._ssh_session = session
        self._cache = []

    def __pgrep_incognito(self):
        cmd = 'pgrep incognito -a'
        pgrep_data = self._ssh_session.send_cmd(cmd)
        return pgrep_data

    def __get_working_dir(self):
        """
        @return: Absolute path to working dir
        """
        try:
            return self._cache['dir']
        except KeyError:
            raise ValueError('Not found working directory in cache, must run find_pid_by_rpc_port first')

    def __find_cmd_full_line(self, rpc_port):
        regex = re.compile(
            r'--rpclisten (localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):'
            f'{rpc_port}', re.IGNORECASE)
        for line in self.__pgrep_incognito():
            if re.findall(regex, line):
                return line.split()
        logger.debug(f'Not found any Incognito process running with rpc port {rpc_port}')

    def __find_run_command(self, rpc_port):
        """
        @return: string
        """
        return ' '.join(self.__find_cmd_full_line(rpc_port)[1:])

    def __get_data_dir(self, rpc_port):
        """
        @return: data dir, relative to working dir
        """
        full_cmd = self.__find_run_command(rpc_port)
        pattern = re.compile(r"--datadir \w+/(\w+)")
        return re.findall(pattern, full_cmd)[0]

    def get_mining_key(self, rpc_port):
        command = self.__find_run_command(rpc_port)
        pattern = re.compile(r"--miningkeys \"*(\w+)\"*")
        try:
            return re.findall(pattern, command)[0]
        except IndexError:
            return None

    def __goto_working_dir(self, rpc_port):
        return self._ssh_session.goto_folder(self.__get_working_dir(rpc_port))

    def __goto_data_dir(self, rpc_port):
        return self._ssh_session.goto_folder(f'{self.__get_working_dir(rpc_port)}/{self.__get_data_dir()}')

    def find_pid(self, rpc_port):
        """
        get process id base on rpc port of the node
        @return:
        """
        try:
            pid = self._cache['cmd'][0]
        except KeyError:
            pid = self.__find_cmd_full_line(rpc_port)[0]

        # find working dir if not yet found
        try:
            self._cache['dir']
        except KeyError:
            cmd = f'pwdx {pid}'
            result = self._ssh_session.send_cmd(cmd)
            if result[1] != 'No such process':
                self._cache['dir'] = result[1].split()[1]

        return pid

    def start_node(self):
        cmd = self.__find_run_command()
        folder = self.__get_working_dir()
        self._ssh_session.send_cmd(f'cd {folder}')
        return self._ssh_session.send_cmd(f'{cmd} >> logs/{self.get_log_file()} 2> logs/{self.get_error_log_file()} &')

    def kill_node(self):
        return self._ssh_session.send_cmd(f'kill {self.find_pid()}')

    def is_node_alive(self):
        cmd = f'[ -d "/proc/{self.find_pid()}" ] && echo 1 || echo 0'
        return bool(int(self._ssh_session.send_cmd(cmd)[1][0]))

    def clear_data(self):
        if self.is_node_alive():
            raise IOError(f'Cannot clear data when process is running')
        self.__goto_data_dir()
        return self._ssh_session.send_cmd(f'rm -Rf *')

    def get_log_folder(self):
        return f"{self.__get_working_dir()}/logs"

    def get_log_file(self):
        # when build chain, the log file name must be the same as data dir name
        # if encounter problem here, check your build config again
        data_path = self.__get_data_dir()
        data_dir_name = data_path.split('/')[-1]
        return f"{data_dir_name}.log"

    def get_error_log_file(self):
        # when build chain, the log file name must be the same as data dir name
        # if encounter problem here, check your build config again
        data_path = self.__get_data_dir()
        data_dir_name = data_path.split('/')[-1]
        return f"{data_dir_name}_error.log"

    def log_tail_grep(self, grep_pattern, tail_option=''):
        """
        @param grep_pattern:
        @param tail_option: careful with this, -f might cause serious problem when not handling correctly afterward
        @return: output of tail command
        """
        tail_cmd = f'tail {tail_option} {self.get_log_file()} | grep {grep_pattern}'
        return self._ssh_session.send_cmd(tail_cmd)

    def log_cat_grep(self, grep_pattern):
        """

        @param grep_pattern:
        @return: output of cat command
        """
        cat_cmd = f'cat {self.get_log_file()} | grep {grep_pattern}'
        return self._ssh_session.send_cmd(cat_cmd)

    def shell(self):
        return self._ssh_session

import stem.process
from stem.util import term
from stem import Signal
from stem.control import Controller

from psutil import process_iter
from signal import SIGTERM

class TorManager(object):
    
    def __init__(self, socks_port, control_port, calls_to_change=10):
        self.socks_port = socks_port
        self.control_port = control_port
        self.calls_to_change = calls_to_change
        
        self.tor_process = self._create_tor_process()
        self.calls_counter = 0

    def __del__(self):
        self._close_tor_process()

    def _close_tor_process(self):
        if hasattr(self, 'tor_process'):
            self.tor_process.terminate()
            self.tor_process.wait()

    def new_identity(self):
        with Controller.from_port(port=self.control_port) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)

    def _print_bootstrap_lines(self, line):
        if "Bootstrapped " in line:
            print(term.format(line, term.Color.BLUE))

    def _create_tor_process(self):
        try:
            tor_process = stem.process.launch_tor_with_config(
                config = {
                    'SocksPort': str(self.socks_port),
                    'ControlPort': str(self.control_port),
                    'DataDirectory': '/tmp/tor'+str(self.socks_port),
                },
                init_msg_handler = self._print_bootstrap_lines,
                )
                
            return tor_process
        except OSError as ex:
            if 'Failed to bind one of the listener ports.' not in str(ex): raise

            for proc in process_iter():
                if proc.name() == 'tor':
                    for conns in proc.connections(kind='inet'):
                        if conns.laddr[1] == self.socks_port:
                            proc.send_signal(SIGTERM)
                            return self._create_tor_process()

            raise
        
    def call_for_new_ip(self, *args, **kwargs):
        self.calls_counter += 1
        if self.calls_counter % self.calls_to_change == 0:
            self.new_identity()
    
    @property
    def proxies(self):
        proxies = {'http': 'socks5://127.0.0.1:%d' % self.socks_port, 'https': 'socks5://127.0.0.1:%d' % self.socks_port}
        return proxies

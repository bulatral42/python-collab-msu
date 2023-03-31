import cmd
import shlex
import threading
import socket
import readline
import select


MAX_MSG_SIZE = 4096


class CowSpeaker(cmd.Cmd):
    intro = "Entering Cow Chat"
    prompt = "moo? "

    _sock = None
    _online = False

    _lock = threading.Lock()

    def __init__(self, socket):
        super().__init__()
        self._sock = socket

    def connect(self, ip, port):
        self._sock.connect((ip, port))
        self._sock.setblocking(False)

    def send(self, msg):
        self._sock.send(msg.encode())

    def recv_msg(self, tmt):
        if self._sock.fileno() == -1:
            return None
        ready_to_read, _, _ = select.select([self._sock], [], [], tmt)
        for s in ready_to_read:
            msg = s.recv(MAX_MSG_SIZE).decode()
            if msg:
                return msg.strip().replace('\t', '\n')
        return 0

    def do_who(self, args):
        self.send('who\n')

    def do_cows(self, args):
        self.send('cows\n')

    def do_login(self, args):
        parsed = shlex.split(args)
        name = parsed[0] if len(parsed) > 0 else ''
        self.send(f'login {name}\n')
        self._online = True

    def complete_login(self, text, line, begidx, endidx):
        variants = []
        with self._lock:
            self.send('CMD cows\n')
            msg = self.recv_msg(None)[4:]
            cows = msg.split(', ')
            variants = []
            for cow in cows:
                if cow.startswith(text):
                    variants.append(cow)
        return variants

    def do_say(self, args):
        parsed = shlex.split(args)
        if len(parsed) < 2:
            parsed += ['', '']
        name, msg = parsed[:2]
        self.send(f'say {name} {msg}\n')

    def complete_say(self, text, line, begidx, endidx):
        with self._lock:
            args = shlex.split(line)
            if len(args) <= 2:
                self.send('CMD who\n')
                msg = self.recv_msg(None)[4:]
                cows = msg.split(', ')
                variants = []
                for cow in cows:
                    if cow.startswith(text):
                        variants.append(cow)
            else:
                variants = []
        return variants

    def do_yield(self, args):
        parsed = shlex.split(args)
        if len(parsed) < 1:
            parsed.append('')
        msg = parsed[0]
        self.send(f'yield {msg}\n')

    def do_quit(self, args):
        self.send('quit\n')
        self._online = False
        self._sock.close()
        print('\n', end='')
        return True

    def precmd(self, line):
        if line == 'EOF':
            return 'quit'
        return line

    def online(self):
        return self._online

    def receiver(self):
        while True:
            with self._lock:
                msg = self.recv_msg(0.0)
                if msg is None:
                    break
                if msg != 0:
                    if len(msg) < len(self.prompt):
                        msg += ' ' * (len(self.prompt) - len(msg))
                    print(f"\r{msg}\n{self.prompt}{readline.get_line_buffer()}", end="", flush=True)


if __name__ == '__main__':
    ip = '0.0.0.0'
    port = 1337

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        cmdline = CowSpeaker(sock)
        cmdline.connect(ip, port)
        recv_t = threading.Thread(target=cmdline.receiver)
        recv_t.start()

        cmdline.cmdloop()

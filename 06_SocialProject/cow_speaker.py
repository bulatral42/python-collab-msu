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
    _cmd_buf = []


    def __init__(self, socket):
        super().__init__()
        self._sock = socket

    def connect(self, ip, port):
        self._sock.connect((ip, port))
        self._sock.setblocking(False)
        print('connected', flush=True)

    def send_msg(self, msg):
        self._sock.send(msg.encode())

    def send_cmd(self, cmd):
        self._sock.send(('CMD ' + msg).encode())

    def recv_msg(self, tmt):
        ready_to_read, _, _ = select.select([self._sock], [], [], tmt)
        for s in ready_to_read:
            msg = s.recv(MAX_MSG_SIZE).decode()
            if msg.startswith('CMD '):
                msg = msg[4:]
                with self._lock:
                    self._cmd_buf.append(msg)
                print(f"\nCMD ANS: {msg}\n{self.prompt}{readline.get_line_buffer()}", end="", flush=True)
            else:
                print(f"\n{msg}\n{self.prompt}{self.get_line_buffer()}", end="", flush=True)

    def do_who(self, args):
        self.send('who\n')

    def do_cows(self, args):
        self.send('cows\n')

    def do_login(self, args):
        parsed = shlex.parse(args)
        name = parsed[0] if len(parsed) > 0 else ''
        self.send(f'login {name}\n')
        self._online = True

    def complete_login(self, args):
        pass

    def do_say(self, args):
        parsed = shlex.parse(args)
        if len(parsed) < 2:
            parsed += ['', '']
        name, msg = parsed[:2]
        self.send(f'say {name} {msg}\n')

    def complete_say(self, args):
        pass

    def do_yield(self, args):
        parsed = shlex.parse(args)
        if len(parsed) < 1:
            parsed.append('')
        msg = parsed[0]
        self.send(f'yield {msg}\n')

    def do_quit(self, args):
        self.send('quit\n')
        self._online = False

    def online(self):
        return self._online

    def receiver(self):
        while self._online:
            self.recv_msg(0.0)


if __name__ == '__main__':
    ip = '0.0.0.0'
    port = 1337

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        cmdline = CowSpeaker(sock)
        cmdline.connect(ip, port)
        recv_t = threading.Thread(target=cmdline.receiver)
        recv_t.start()

        cmdline.cmdloop()

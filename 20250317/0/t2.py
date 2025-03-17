import cmd
import sys
import socket


class chat(cmd.Cmd):
    prompt='>>'

    def __init__(self, completekey = "tab", stdin = None, stdout = None):
        super().__init__(completekey, stdin, stdout)

    def do_print(self, arg):
        print(f'ARRRRRRRRR = {arg}')

    def do_info(self, args):
        pass

    def complete_info(self, text, line, begidx, endidx):
        words = (line[:endidx] + ".").split()
        DICT = []
        match len(words):
            case 2:
                DICT = ANY
            case 3:
                if words[1] in DECS:
                    DICT = DIGITS
        words[-1] = words[-1].replace('.','')
        return [c for c in DICT if c.startswith(text)]

host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    while msg := sys.stdin.buffer.readline():
        s.sendall(msg)
        print(s.recv(1024).rstrip().decode())
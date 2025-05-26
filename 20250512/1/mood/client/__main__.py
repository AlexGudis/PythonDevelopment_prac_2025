"""Client"""

import time
from . import Client

import sys
import socket
import threading
import locale
import os
import gettext


localedir = os.path.join(os.path.dirname(__file__), "locales")

LOCALES = {
    ("ru_RU", "UTF-8"): gettext.translation("messages", localedir, ["ru"]),
    ("en_US", "UTF-8"): gettext.NullTranslations()
}
locale.setlocale(locale.LC_CTYPE, locale.getdefaultlocale())

gamer_loca = ("en_US", "UTF-8")


def _(text):
    return LOCALES[locale.getlocale()].gettext(text)

def run_client():
    """Run client"""
    if len(sys.argv) > 3 and sys.argv[2] == '--file':
        file = open(sys.argv[3])
    else:
        file = None
    host = "localhost"
    port = 1337
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((host, port))
    s.sendall(f"{sys.argv[1]}\n".encode())
    if s.recv(1024).rstrip().decode() == '1':
        print("<<< Welcome to Python-MUD 0.1 >>>")
        print(f"Your login: {sys.argv[1]}")
        if file is None:
            cmdline = Client(socket=s)
        else:
            cmdline = Client(socket=s, stdin=file)
            cmdline.prompt = ''
            cmdline.use_rawinput = False
        mes = threading.Thread(target=cmdline.from_srv, args=(cmdline, s))
        mes.start()
        cmdline.cmdloop()
    else:
        print("ERROR: Choose another login")
    s.shutdown(socket.SHUT_RDWR)
    if file:
        file.close()


if __name__ == '__main__':
    run_client()
"""Client"""

import time
from . import *

if __name__ == '__main__':
    host = "localhost"
    port = 1337
    username = None
    filemode = False
    filename = ""

    if '--file' in sys.argv:
        filemode = True
        file_index = sys.argv.index('--file')
        if file_index + 1 >= len(sys.argv):
            print("Ooops: You must specify a file name after --file")
            sys.exit(1)
        filename = sys.argv[file_index + 1]
        username = sys.argv[1]
        if len(sys.argv) > file_index + 2:
            host = sys.argv[file_index + 2]
        if len(sys.argv) > file_index + 3:
            port = int(sys.argv[file_index + 3])
    else:
        username = sys.argv[1]
        if len(sys.argv) > 2:
            host = sys.argv[2]
        if len(sys.argv) > 3:
            port = int(sys.argv[3])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((host, port))
    s.sendall(f"{username}\n".encode())
    
    if s.recv(1024).rstrip().decode() == '1':
        print(f"Your login: {username}")
        cmdline = client(socket=s)
        mes = threading.Thread(target=cmdline.from_srv, args=(cmdline, s))
        mes.start()

        if filemode:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    print(f"Executing: {line}")
                    cmdline.onecmd(line)
                    time.sleep(1)
            cmdline.do_EOF()
            print(_("All commands from file are done. Logout"))
            #cmdline.cmdloop()
        else:
            cmdline.cmdloop()

    else:
        print(_("This login is already assigned"))
    s.shutdown(socket.SHUT_RDWR)
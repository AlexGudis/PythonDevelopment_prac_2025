import sys
import socket


def sqroots(coeffs:str) -> str:
    try:
        a,b,c = map(int, coeffs.split())
    except Exception:
        raise ValueError

    if a == 0:
        raise ValueError
    

    D = b * b - 4 * a * c
    if D == 0:
        return str(-b / (2*a))
    elif D > 0:
        return str((-b + D**0.5) / 2*a) + ' , ' + str((-b - D**0.5) / 2*a)
    else:
        return 'Nothing'
    

def sqrootnet(line, sock):
    sock.sendall( (line + '\n').encode())
    return sock.recv(128).decode().strip()


if __name__ == '__main__':
    match sys.argv:
        case [prog, args]:
            print(sqroots(sys.args))
        case [prog, args, host, port]:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, int(port)))
                print(sqrootnet(args, s))



    
import socket
import threading
import sys
from select import select

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 9090))

    while True:
        readable, writable, exceptional = select([sys.stdin, sock], [], [])
        for s in readable:
            if s == sock:
                data = s.recv(1024)
                if not data:
                    print('close')
                    return
                print(data.decode())
            elif s == sys.stdin:
                data = sys.stdin.readline()
                sock.send(data.encode())

if __name__ == '__main__':
    start_server()
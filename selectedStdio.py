# coding=UTF-8
""" === Windows stdio ===
@author ideawu@163.com
@link http://www.ideawu.net/
File objects on Windows are not acceptable for select(),
this module creates two sockets: stdio.s_in and stdio.s_out,
as pseudo stdin and stdout.

@example
from stdio import stdio
stdio.write('hello world')
data = stdio.read()
print stdio.STDIN_FILENO
print stdio.STDOUT_FILENO
"""
import threading
import sys, os
import socket


# socket read/write in multiple threads may cause unexpected behaviors
# so use two separated sockets for stdin and stdout


def selectedStdio(where=sys):
    def stdin_thread(sock, console):
        """	read data from stdin, and write the data to sock
        """
        try:
            fd = where.stdin.fileno()
            while True:
                # DO NOT use sys.stdin.read(), it is buffered
                data = os.read(fd, 1024)
                # print 'stdin read: ' + repr(data)
                if not data:
                    break
                while True:
                    nleft = len(data)
                    nleft -= sock.send(data)
                    if nleft == 0:
                        break
        except:
            pass
        # print 'stdin_thread exit'
        sock.close()

    def stdout_thread(sock, console):
        """	read data from sock, and write to stdout
        """
        try:
            fd = where.stdout.fileno()
            while True:
                data = sock.recv(1024)
                # print 'stdio_sock recv: ' + repr(data)
                if not data:
                    break
                while True:
                    nleft = len(data)
                    nleft -= os.write(fd, data)
                    if nleft == 0:
                        break
        except:
            pass
        # print 'stdin_thread exit'
        sock.close()

    class Console:
        def __init__(self):
            self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serv.bind(('127.0.0.1', 0))
            self.serv.listen(5)
            port = self.serv.getsockname()[1]

            # data read from stdin will write to this socket
            self.stdin_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.stdin_sock.connect(('127.0.0.1', port))
            self.s_in, addr = self.serv.accept()

            # data read from this socket will write to stdout
            self.stdout_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.stdout_sock.connect(('127.0.0.1', port))
            self.s_out, addr = self.serv.accept()

            self.STDIN_FILENO = self.s_in.fileno()
            self.STDOUT_FILENO = self.s_out.fileno()

            threading.Thread(target=stdin_thread, args=(self.stdin_sock, self)).start()
            threading.Thread(target=stdout_thread, args=(self.stdout_sock, self)).start()

        def close(self):
            self.s_in.close()
            self.s_out.close()
            self.stdin_sock.close()
            self.stdout_sock.close()
            self.serv.close()

        def write(self, data):
            return self.s_out.send(data)

        def read(self):
            data = self.s_in.recv(4096)
            return data

        def fileno(self):
            return self.STDOUT_FILENO

    stdio = Console()
    return stdio

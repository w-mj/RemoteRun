import subprocess
from select import select
import socket
import argparse


def run_task(task, address, restart):
    print("run task")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(0)
    print('start local server at {}'.format(address))
    subp = subprocess.Popen(task, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    remote_socket = None
    remote_address = None
    inputs = [sock, subp.stdout, subp.stderr]
    while True:
        readable, writable, exceptional = select(inputs, [], [])
        for s in readable:
            if s == sock:
                if remote_address is not None:
                    temp, tempa = sock.accept()
                    print('refuse connect {}'.format(tempa))
                    temp.send("server is already connected on {}".format(remote_address).encode())
                    temp.close()
                else:
                    remote_socket, remote_address = sock.accept()
                    print('remote connected on {}'.format(remote_address))
                    inputs.append(remote_socket)
            elif s == remote_socket:
                data = s.recv(1024)
                if not data:
                    inputs.remove(s)
                    print("remote client {} closed.".format(remote_address))
                    remote_socket = None
                    remote_address = None
                    s.close()
                else:
                    print('remote message: {}'.format(data))
                    subp.stdin.write(data)
                    subp.stdin.flush()
            else:
                if remote_address is not None:
                    data = subp.stdout.readline()
                    if not data:
                        if restart:
                            subp = subprocess.Popen(task, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE)
                        else:
                            remote_socket.send('task closed.'.encode())
                            return
                    print('local response: {}'.format(data))
                    remote_socket.send(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("task", help="要执行的任务")
    parser.add_argument("-a", "--address", help="本地服务器监听地址 ip:port", default="0.0.0.0:9090")
    parser.add_argument("-s", "--autostart", help="任务结束后是否自动重新启动", action="store_true")
    args = parser.parse_args()
    ip = args.address.split(':')
    port = int(ip[1])
    ip = ip[0]
    run_task(args.task.split(), (ip, port), args.autostart)

import base64
import hashlib
import subprocess
from select import select
import socket
import argparse
import struct

magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'


def pack_msg(msg):
    """
    包装成websocket格式
    :param msg: 要包装的数据 bytes
    :return: 包装后的数据 bytes
    """
    token = b"\x81"
    length = len(msg)
    if length < 126:
        token += struct.pack("B", length)
    elif length <= 0xFFFF:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)

    msg = token + msg
    return msg


def unpack_msg(info):
    """
    从websockets格式解包
    :param info: 原始数据 bytes
    :return: 解包后数据部分 bytes
    """
    if info[0] & 0x0f == 8:  # 关闭连接
        return bytes()
    payload_len = info[1] & 127
    if payload_len == 126:
        extend_payload_len = info[2:4]
        mask = info[4:8]
        decoded = info[8:]
    elif payload_len == 127:
        extend_payload_len = info[2:10]
        mask = info[10:14]
        decoded = info[14:]
    else:
        extend_payload_len = None
        mask = info[2:6]
        decoded = info[6:]

    bytes_list = bytearray()
    for i in range(len(decoded)):
        chunk = decoded[i] ^ mask[i % 4]
        bytes_list.append(chunk)
    return bytes(bytes_list)


def get_headers(data):
    header_dict = {}
    data = str(data, encoding='utf-8')
    header, body = data.split('\r\n\r\n', 1)
    header_list = header.split('\r\n')
    for i in range(0, len(header_list)):
        if i == 0:
            if len(header_list[i].split(' ')) == 3:
                header_dict['method'], header_dict['url'], header_dict['protocol'] = header_list[i].split(' ')
        else:
            k, v = header_list[i].split(':', 1)
            header_dict[k] = v.strip()
    return header_dict


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
            if s == sock:  # connect
                if remote_address is not None:
                    temp, tempa = sock.accept()
                    print('refuse connect {}'.format(tempa))
                    temp.send("server is already connected on {}".format(remote_address).encode())
                    temp.close()
                else:
                    remote_socket, remote_address = sock.accept()
                    print('remote connected on {}'.format(remote_address))
                    data = remote_socket.recv(4096)
                    headers = get_headers(data)  # 提取请求头信息
                    # 对请求头中的sec-websocket-key进行加密
                    response_tpl = "HTTP/1.1 101 Switching Protocols\r\n" \
                                   "Upgrade:websocket\r\n" \
                                   "Connection: Upgrade\r\n" \
                                   "Sec-WebSocket-Accept: %s\r\n" \
                                   "WebSocket-Location: ws://%s%s\r\n\r\n"
                    value = headers['Sec-WebSocket-Key'] + magic_string
                    ac = base64.b64encode(hashlib.sha1(value.encode('utf-8')).digest())
                    response_str = response_tpl % (ac.decode('utf-8'), headers['Host'], headers['url'])
                    # 响应【握手】信息
                    remote_socket.send(bytes(response_str, encoding='utf-8'))
                    inputs.append(remote_socket)
            elif s == remote_socket:  # receive
                data = s.recv(8096)
                if not data:
                    inputs.remove(s)
                    print("remote client {} closed.".format(remote_address))
                    remote_socket = None
                    remote_address = None
                    s.close()
                else:
                    print(data)
                    data = unpack_msg(data)
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
                            print("task closed")
                            remote_socket.send(pack_msg('task closed.'.encode()))
                            return
                    print('local response: {}'.format(data))
                    remote_socket.send(pack_msg(data))


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

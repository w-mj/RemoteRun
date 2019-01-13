import argparse
from server import Server
from threading import Thread
from Http import Http

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("task", help="要执行的任务")
    parser.add_argument("-a", "--address", help="本地服务器监听地址 ip:port", default="0.0.0.0:9090")
    parser.add_argument("-s", "--autostart", help="任务结束后是否自动重新启动", action="store_true")
    parser.add_argument("-m", "--method", required=False, choices=["socket", "websocket", "http"], help="指定以socket、websocket或http方式传输信息，默认为socket。", default="s")
    args = parser.parse_args()
    ip = args.address.split(':')
    port = int(ip[1])
    ip = ip[0]
    if args.method == "h":
        s = Server()
        Thread(target=s.run_task, args=(args.task.split(), ('127.0.0.1', 0), args.autostart)).start()
        local_port = s.port
        while local_port == 0:
            local_port = s.port
        hs = Http(('127.0.0.1', local_port), (ip, port))
    else:
        s = Server()
        s.ws = args.method == "w"
        s.run_task(args.task.split(), (ip, port), args.autostart)

from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from socketserver import ThreadingMixIn
local_socket = None


class Http:

    class MyHttpServer(BaseHTTPRequestHandler):
        def do_POST(self):
            if local_socket is None:
                self.send_response(403)
            else:
                data = self.rfile.read(int(self.headers['content-length']))
                local_socket.send(data)
                rdata = local_socket.recv(1024)
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(rdata)

    class ThreadingHttpServer(ThreadingMixIn, HTTPServer):
        pass

    def __init__(self, addr, listen_addr):
        global local_socket
        local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_socket.connect(addr)
        local_socket.recv(1024)
        server = self.ThreadingHttpServer(listen_addr, self.MyHttpServer)
        # server = HTTPServer(listen_addr, self.MyHttpServer)
        print('Start Http server at {}'.format(listen_addr))
        server.serve_forever()

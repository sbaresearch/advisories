import SocketServer

DATA = "Registrant Name: ${passthru('id')}\n"

class WhoisHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.request.recv(1024)
        print('Request received')
        self.request.sendall(DATA)
        print('Payload sent')

if __name__ == '__main__':
    SocketServer.ThreadingTCPServer.allow_reuse_address = True
    server = SocketServer.ThreadingTCPServer(('127.0.0.1', 9999), WhoisHandler)
    server.serve_forever()

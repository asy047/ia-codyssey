import argparse
from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from datetime import datetime

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        ip = self.client_address[0]
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'접속 시간: {now} | IP: {ip}')
        super().do_GET()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server(host, port):
    server_address = (host, port)
    httpd = ThreadedHTTPServer(server_address, CustomHandler)
    print(f'http://{host}:{port} 에서 서버 실행 중...')
    httpd.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()

    run_server(args.host, args.port)

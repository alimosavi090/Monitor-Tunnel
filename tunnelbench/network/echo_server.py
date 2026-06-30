"""
Lightweight Echo Server for point-to-point speed testing.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from tunnelbench.core.logger import log

class EchoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/download":
            qs = parse_qs(parsed_url.query)
            size_mb = 2
            if "size_mb" in qs:
                try:
                    size_mb = int(qs["size_mb"][0])
                except ValueError:
                    pass
            
            bytes_to_send = size_mb * 1024 * 1024
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Length', str(bytes_to_send))
            self.end_headers()
            
            chunk_size = 65536
            dummy_data = b"0" * chunk_size
            sent = 0
            while sent < bytes_to_send:
                send_len = min(chunk_size, bytes_to_send - sent)
                try:
                    self.wfile.write(dummy_data[:send_len])
                except (BrokenPipeError, ConnectionResetError):
                    break
                sent += send_len
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/upload":
            content_length = int(self.headers.get('Content-Length', 0))
            self.send_response(200)
            self.end_headers()
            
            chunk_size = 65536
            received = 0
            while received < content_length:
                read_len = min(chunk_size, content_length - received)
                try:
                    chunk = self.rfile.read(read_len)
                    if not chunk:
                        break
                    received += len(chunk)
                except Exception:
                    break
                    
            try:
                self.wfile.write(b"OK")
            except Exception:
                pass
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        # Disable default HTTP logging to avoid clutter
        pass

def run_echo_server(port: int = 8080):
    server_address = ('0.0.0.0', port)
    httpd = ThreadingHTTPServer(server_address, EchoHandler)
    log.info(f"Started TunnelBench Point-to-Point Server on 0.0.0.0:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        log.info("Shutting down Point-to-Point Server...")
        httpd.server_close()

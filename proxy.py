from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import sys
from request import get
def loadpage(file):
    # Construct the file path
    path = os.path.dirname(sys.argv[0])
    file_path = os.path.join(path, "base", file)
    try:
        with open(file_path, "r") as f:
            # Read and encode the file content
            return f.read().encode('utf-8')
    except FileNotFoundError:
        # Return a default 404 message if the file is not found
        return b""

class SimpleWebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # Respond based on the requested path
        if self.path == '/':
            content = loadpage("home.html")
        else:
            
            send = f"you went to {self.path} "
            content = send.encode('utf-8')

        # If no 404 occurred, send a 200 response
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content)

def run(server_class=HTTPServer, handler_class=SimpleWebServer, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run(port=801)

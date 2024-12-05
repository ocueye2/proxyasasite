from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import sys
from urllib.parse import urljoin, urlparse, unquote
from requests import get
from bs4 import BeautifulSoup  # For HTML parsing


def load_page(file):
    """
    Load an HTML file from the 'base' directory.
    """
    path = os.path.dirname(sys.argv[0])
    file_path = os.path.join(path, "base", file)
    try:
        with open(file_path, "rb") as f:
            return f.read()  # Return raw bytes for non-HTML files
    except FileNotFoundError:
        return None  # Return None if the file is not found


def rewrite_urls(html_content, base_url):
    """
    Rewrite all relative URLs in the HTML content to absolute paths prefixed with '/'.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    parsed_base = urlparse(base_url)

    # Rewrite <a> tags
    for tag in soup.find_all('a', href=True):
        original_url = tag['href']
        full_url = urljoin(base_url, original_url)  # Resolve relative URL
        rewritten_url = f"/https://{parsed_base.netloc}{urlparse(full_url).path}"
        print(f"Rewriting <a>: {original_url} -> {rewritten_url}")
        tag['href'] = rewritten_url

    # Rewrite <img> tags
    for tag in soup.find_all('img', src=True):
        original_url = tag['src']
        full_url = urljoin(base_url, original_url)  # Resolve relative URL
        rewritten_url = f"/https://{parsed_base.netloc}{urlparse(full_url).path}"
        print(f"Rewriting <img>: {original_url} -> {rewritten_url}")
        tag['src'] = rewritten_url

    # Rewrite <link> tags
    for tag in soup.find_all('link', href=True):
        original_url = tag['href']
        full_url = urljoin(base_url, original_url)  # Resolve relative URL
        rewritten_url = f"/https://{parsed_base.netloc}{urlparse(full_url).path}"
        print(f"Rewriting <link>: {original_url} -> {rewritten_url}")
        tag['href'] = rewritten_url

    # Rewrite <script> tags
    for tag in soup.find_all('script', src=True):
        original_url = tag['src']
        full_url = urljoin(base_url, original_url)  # Resolve relative URL
        rewritten_url = f"/https://{parsed_base.netloc}{urlparse(full_url).path}"
        print(f"Rewriting <script>: {original_url} -> {rewritten_url}")
        tag['src'] = rewritten_url

    return str(soup)


class SimpleWebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Handle GET requests.
        """
        if self.path == '/':
            content = load_page("home.html")
            if content is None:
                self.send_error(404, "Home page not found")
                return

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(content)

        elif self.path.startswith('/stop'):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Server stopping...")
            os._exit(0)  # Stop the server

        else:
            # Proxy external URLs
            url = unquote(self.path[1:])
            print(f"Proxying request for URL: {url}")
            try:
                response = get(url, stream=True)
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', 'application/octet-stream')
                    print(f"Fetched URL {url} with Content-Type: {content_type}")
                    self.send_response(200)
                    self.send_header('Content-Type', content_type)
                    self.end_headers()

                    if 'text/html' in content_type:
                        rewritten_html = rewrite_urls(response.text, url)
                        self.wfile.write(rewritten_html.encode('utf-8'))
                    elif 'image/' in content_type:
                        # Handle binary image content directly
                        for chunk in response.iter_content(chunk_size=8192):
                            self.wfile.write(chunk)
                    else:
                        # Handle non-HTML, non-image binary content
                        for chunk in response.iter_content(chunk_size=8192):
                            self.wfile.write(chunk)
                else:
                    print(f"Failed to fetch URL {url}, Status Code: {response.status_code}")
                    self.send_error(response.status_code, f"Error fetching URL: {url}")
            except Exception as e:
                print(f"Exception fetching URL {url}: {e}")
                self.send_error(500, f"Failed to fetch URL: {e}")

    def log_message(self, format, *args):
        """
        Suppress logging to keep the console clean.
        """
        return


def run(server_class=HTTPServer, handler_class=SimpleWebServer, port=802):
    """
    Run the HTTP server.
    """
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()


if __name__ == '__main__':
    run()

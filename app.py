from http.server import BaseHTTPRequestHandler, HTTPServer


class TestpressHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        message = b"Hello from Testpress!"

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(message)))
        self.end_headers()

        self.wfile.write(message)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), TestpressHandler)

    print("Testpress server running on port 8080")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.server_close()

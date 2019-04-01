# coding: utf-8
"""An HTTP server to detect the local web browser.
"""

import contextlib
import socket
import threading
import queue
import webbrowser

import six
import pkg_resources

class UserAgentRequestHandler(six.moves.BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        """Serve a GET request."""
        self.do_HEAD()
        template = pkg_resources.resource_string(__name__, "static/splash.html")
        page = template.decode('utf-8').format(self.headers.get("User-Agent"), self.cache)
        self.wfile.write(page.encode('utf-8'))

    def do_HEAD(self):
        """Serve a HEAD request."""
        self.queue.put(self.headers.get("User-Agent"))
        self.send_response(six.moves.BaseHTTPServer.HTTPStatus.OK)
        self.send_header("Location", self.path)
        self.end_headers()

    def log_message(self, format, *args):
        pass # silence the server


def get_free_port():
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def get_user_agent(port=None, cache=None):
    # Setup thread-local request handler
    UserAgentRequestHandler.queue = queue.Queue()
    UserAgentRequestHandler.cache = cache
    # Lock the request handler lock to wait for user agent to be processed.
    # Use the given port or get a free one and create the HTTP server
    port = port or get_free_port()
    server = six.moves.BaseHTTPServer.HTTPServer(
        ("localhost", port),
        UserAgentRequestHandler,
    )
    # Launch the server thread in the background
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    # Use webbrowser to connect to the server with the default browser
    webbrowser.open("http://localhost:{}/".format(port))
    # Wait for the request handler to get the request from the browser
    user_agent = UserAgentRequestHandler.queue.get()
    # Close the server
    server.shutdown()
    server.server_close()
    # Return the obtained user agent
    return user_agent


if __name__ == "__main__":
    print(get_user_agent())

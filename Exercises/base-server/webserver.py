from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs


class WebServerHandler(BaseHTTPRequestHandler):
    # Class variable to hold the message. Each request generates a new
    # RequestHandler instance
    message = 'Hello?'

    def do_GET(self):
        try:
            if self.path.endswith('/hello'):
                output = '''
                <html>
                    <body>
                        <p>How about this?</p>
                        <p>{}</p>
                        <form action='/hello' method='post'>
                            <label>Message:</label>
                            <input type='text' name='message'></input><br/>
                            <input type='submit'></input>
                        </form>
                    </body>
                </html>
                '''.format(WebServerHandler.message)
                output = output.encode()

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Content-length', len(output))
                self.end_headers()

                self.wfile.write(output)
                return

            raise IOError()

        except IOError:
            self.send_error(404, 'File not found {}'.format(self.path))


    def do_POST(self):
        # Extract the post message
        post_len = int(self.headers.get('Content-length', 0))
        post_data = self.rfile.read(post_len).decode()
        post_params = parse_qs(post_data)
        if 'message' not in post_params:
            return self.send_error(
                400,
                message='Bad Request',
                explain='Parameter "message" is required.'
            )
        # global message
        WebServerHandler.message = post_params['message'][0]

        # Redirect to form page
        self.send_response(301)
        self.send_header('Location', '/hello')
        self.end_headers()
        return


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print('Web server running on port {}'.format(port))
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C entered, stopping web server')
        pass


if __name__ == '__main__':
    main()

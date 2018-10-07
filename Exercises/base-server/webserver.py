from http.server import BaseHTTPRequestHandler, HTTPServer


class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith('/hello'):
                output = '''
                <html><body>Hello!</body></html>
                '''
                output = output.encode()

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Content-length', len(output))
                self.end_headers()

                self.wfile.write(output)
                return

            if self.path.endswith('/hola'):
                output = '''
                <html>
                    <body>
                        <p>&iexcl;Hola!</p>
                        <p><a href='/hello'>Say Hello</a></p>
                    </body>
                </html>
                '''
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

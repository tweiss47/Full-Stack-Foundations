from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


class WebServerHandler(BaseHTTPRequestHandler):

    def renderRestaurantsPage(self):
        restaurants_template = '''
        <html>
            <head>
                <title>Restaurants</title>
            </head>
            <body>
                <h1>Restaurants</h1>
                <p><a href='/restaurants/new'></a></p>
                {}
            </body>
        </html>'''

        # Get the list of restaurants from the database
        # Initialize the db session
        engine = create_engine('sqlite:///restaurantmenu.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind = engine)
        session = DBSession()

        # Build a list of the restaurant items to output
        restaurant_list = ''
        rows = session.query(Restaurant).order_by(Restaurant.name)
        for row in rows:
            restaurant_list += '''
            <p>{}<br/>
            <a href='#'>Edit</a>
            <a href='#'>Delete</a>
            </p>
            '''.format(row.name)

        # Clean up the db session
        session.close()

        # build and encode the response
        output = restaurants_template.format(restaurant_list)
        return output.encode()


    def sendResponse(self, output, type='text/html'):
        self.send_response(200)
        self.send_header('Content-type', type)
        self.send_header('Content-length', len(output))
        self.end_headers()
        self.wfile.write(output)


    def do_GET(self):
        try:
            if self.path.endswith('/restaurants'):
                output = self.renderRestaurantsPage()
                self.sendResponse(output)
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

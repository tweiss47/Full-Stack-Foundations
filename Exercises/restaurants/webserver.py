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
                <p><a href='/restaurants/new'>Add a New Restaurant</a></p>
                {}
            </body>
        </html>'''

        # Get the list of restaurants from the database
        session = self.getDbSession()

        # Build a list of the restaurant items to output
        restaurant_list = ''
        rows = session.query(Restaurant).order_by(Restaurant.name)
        for row in rows:
            restaurant_list += '''
            <p>{}<br/>
            <a href='/restaurants/{}/edit'>Edit</a>
            <a href='/restaurants/{}/delete'>Delete</a>
            </p>
            '''.format(row.name, row.id, row.id)

        # Clean up the db session
        session.close()

        # build and encode the response
        output = restaurants_template.format(restaurant_list)
        return output.encode()


    def renderAddRestaurantPage(self):
        output = '''
        <html>
            <head>
                <title>Add a Restaurant</title>
            </head>
            <body>
                <h1>Add a New Restaurant</h1>
                <form action='/restaurant/add' method='post'>
                    <label>Name:</label>
                    <input type='text' name='name'></input><br/>
                    <input type='submit'></input>
                </form>
            </body>
        </html>'''
        return output.encode()


    def renderEditRestaurantPage(self, id):
        edit_template = '''
        <html>
            <head>
                <title>Edit a Restaurant</title>
            </head>
            <body>
                <h1>Edit a Restaurant</h1>
                <form action='/restaurant/edit' method='post'>
                    <label>Name:</label>
                    <input type='text' name='name' value='{}'/><br/>
                    <input type='submit'/>
                    <input type='hidden' name='id' value='{}'/>
                </form>
            </body>
        </html>'''

        session = self.getDbSession()
        restaurant = session.query(Restaurant).filter_by(id = id).one()
        name = restaurant.name
        session.close()

        output = edit_template.format(name, id)
        return output.encode()


    def renderDeleteRestaurantPage(self, id):
        delete_template = '''
        <html>
            <head>
                <title>Delete a Restaurant</title>
            </head>
            <body>
                <h1>Are you sure you want to delete "{}"</h1>
                <form action='/restaurant/delete' method='post'>
                    <input type='submit'/>
                    <input type='hidden' name='id' value='{}'/>
                </form>
            </body>
        </html>'''

        session = self.getDbSession()
        restaurant = session.query(Restaurant).filter_by(id = id).one()
        name = restaurant.name
        session.close()

        output = delete_template.format(name, id)
        return output.encode()


    def sendResponse(self, output, type='text/html'):
        self.send_response(200)
        self.send_header('Content-type', type)
        self.send_header('Content-length', len(output))
        self.end_headers()
        self.wfile.write(output)


    def getDbSession(self):
        # Initialize the db session
        engine = create_engine('sqlite:///restaurantmenu.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind = engine)
        return DBSession()


    def do_GET(self):
        try:
            if self.path.endswith('/restaurants'):
                output = self.renderRestaurantsPage()
                self.sendResponse(output)
                return

            if self.path.endswith('/restaurants/new'):
                output = self.renderAddRestaurantPage()
                self.sendResponse(output)
                return

            if self.path.endswith('/edit'):
                id = int(self.path.split('/')[-2])
                output = self.renderEditRestaurantPage(id)
                self.sendResponse(output)
                return

            if self.path.endswith('/delete'):
                id = int(self.path.split('/')[-2])
                output = self.renderDeleteRestaurantPage(id)
                self.sendResponse(output)
                return

            raise IOError()

        except IOError:
            self.send_error(404, 'File not found {}'.format(self.path))


    def do_POST(self):
        try:
            # Extract the post message
            post_len = int(self.headers.get('Content-length', 0))
            post_data = self.rfile.read(post_len).decode()
            post_params = parse_qs(post_data)

            if self.path.endswith('/restaurant/add'):
                if 'name' not in post_params:
                    return self.send_error(
                        400,
                        message='Bad Request',
                        explain='Missing parameter values in POST'
                    )

                name = post_params['name'][0]

                session = self.getDbSession()
                session.add(Restaurant(name = name))
                session.commit()
                session.close()

                # Redirect to restaurant list page
                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return

            if self.path.endswith('/restaurant/edit'):
                if 'name' not in post_params or 'id' not in post_params:
                    return self.send_error(
                        400,
                        message='Bad Request',
                        explain='Missing parameter values in POST'
                    )

                name = post_params['name'][0]
                id = int(post_params['id'][0])
                session = self.getDbSession()
                restaurant = session.query(Restaurant).filter_by(id = id).one()
                restaurant.name = name
                session.add(restaurant)
                session.commit()
                session.close()

                # Redirect to restaurant list page
                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return

            if self.path.endswith('/restaurant/delete'):
                if 'id' not in post_params:
                    return self.send_error(
                        400,
                        message='Bad Request',
                        explain='Missing parameter values in POST'
                    )

                id = int(post_params['id'][0])
                session = self.getDbSession()
                restaurant = session.query(Restaurant).filter_by(id = id).one()
                session.delete(restaurant)
                session.commit()
                session.close()

                # Redirect to restaurant list page
                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()
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

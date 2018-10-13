from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

def getDbSession():
    # Initialize a db session
    engine = create_engine('sqlite:///restaurantmenu.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind = engine)
    return DBSession()

app = Flask(__name__)

@app.route('/')
@app.route('/restaurants')
def HandleRestaurants():
    output = ''
    session = getDbSession()
    rows = session.query(Restaurant).order_by(Restaurant.name)
    for row in rows:
        output += row.name + '<br/>'
    session.close()
    return output


@app.route('/restaurants/<int:restaurant_id>')
def HandleMenuItems2(restaurant_id):
    session = getDbSession()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return render_template('menu.html', restaurant = restaurant, menu = menu)


if __name__ == '__main__':
    app.debug = True
    app.run() # default to localhost:5000
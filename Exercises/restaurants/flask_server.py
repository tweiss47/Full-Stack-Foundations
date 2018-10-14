from flask import Flask, render_template, url_for, request, redirect
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
def restaurants():
    output = ''
    session = getDbSession()
    rows = session.query(Restaurant).order_by(Restaurant.name)
    for row in rows:
        output += row.name + '<br/>'
    session.close()
    return output


@app.route('/restaurants/<int:restaurant_id>')
def menu_items(restaurant_id):
    session = getDbSession()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return render_template(
        'menu.html',
        restaurant = restaurant,
        menu = menu
    )


@app.route('/restaurants/<int:restaurant_id>/<int:menu_item_id>/edit', methods=['GET', 'POST'])
def edit_menu_item(restaurant_id, menu_item_id):
    session = getDbSession()
    menu_item = session.query(MenuItem).filter_by(id=menu_item_id).one()
    if request.method == 'POST':
        menu_item.name = request.form['name']
        session.add(menu_item)
        session.commit()
        return redirect(url_for('menu_items', restaurant_id = restaurant_id))
    else:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        return render_template(
            'edit.html',
            restaurant = restaurant,
            item = menu_item
        )


@app.route('/restaurants/<int:restaurant_id>/<int:menu_item_id>/delete')
def delete_menu_item(restaurant_id, menu_item_id):
    return 'Delete menu item {} for {}'.format(menu_item_id, restaurant_id)

if __name__ == '__main__':
    app.debug = True
    app.run() # default to localhost:5000
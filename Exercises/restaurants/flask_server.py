from flask import Flask, render_template, url_for, request, redirect, flash
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
    output = render_template( 'menu.html', restaurant = restaurant, menu = menu)
    session.close()
    return output


@app.route('/restaurants/<int:restaurant_id>/<int:menu_item_id>/edit', methods=['GET', 'POST'])
def edit_menu_item(restaurant_id, menu_item_id):
    session = getDbSession()
    menu_item = session.query(MenuItem).filter_by(id=menu_item_id).one()
    if request.method == 'POST':
        old_name = menu_item.name
        new_name = request.form['name']
        menu_item.name = new_name
        session.add(menu_item)
        session.commit()
        session.close()
        flash('{} was renamed to {}'.format(old_name, new_name))
        return redirect(url_for('menu_items', restaurant_id = restaurant_id))
    else:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        output = render_template( 'edit.html', restaurant = restaurant, item = menu_item)
        session.close()
        return output


@app.route('/restaurants/<int:restaurant_id>/<int:menu_item_id>/delete', methods=['GET', 'POST'])
def delete_menu_item(restaurant_id, menu_item_id):
    session = getDbSession()
    menu_item = session.query(MenuItem).filter_by(id=menu_item_id).one()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        old_name = menu_item.name
        session.delete(menu_item)
        session.commit()
        session.close()
        flash('Item {} was deleted'.format(old_name))
        return redirect(url_for('menu_items', restaurant_id = restaurant_id))
    else:
        output = render_template( 'delete.html', restaurant = restaurant, item = menu_item)
        session.close()
        return output

if __name__ == '__main__':
    app.secret_key = 's0m3thing th@t is v3ry s3cr3t'
    app.debug = True
    app.run() # default to localhost:5000
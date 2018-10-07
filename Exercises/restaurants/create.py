
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

pizzaPalace = Restaurant(
    name = 'Pizza Palace'
)
session.add(pizzaPalace)

cheesePizza = MenuItem(
    name = 'Cheese Pizza',
    description = 'Made with all natural mozzarella',
    course = 'Engtree',
    price = '$8.99',
    restaurant = pizzaPalace
)
session.add(cheesePizza)

session.commit()

print(session.query(Restaurant).all())
print(session.query(MenuItem).all())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

# A DBSession() instance establishes all conversations with the database
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Drop all tables
Base.metadata.drop_all()

# Recreate tables
Base.metadata.create_all()

# Add users
User = User(name="VasviNaveena", email="vasavinaveena@gmail.com")
session.add(User)
session.commit()

# Add categories
category1 = Category(name="Cars")
session.add(category1)
session.commit()

category2 = Category(name="Gadgets")
session.add(category2)
session.commit()

category3 = Category(name="Perfumes")
session.add(category3)
session.commit()

category4 = Category(name="Places")
session.add(category4)
session.commit()

category5 = Category(name="Games")
session.add(category5)
session.commit()


# Add items

item = Item(name="Audi R8", description="The Audi R8[2] is a mid-engine,"
            "2-seater sports car,which uses Audi's trademark"
            " quattro permanent all-wheel drive system."
            " It was introduced by the German car manufacturer Audi AG.",
            category_id=category1.id, user_id=User.id)
session.add(item)
session.commit()

item = Item(name="Bugatti Chiron", description="The Bugatti Chiron is a"
            " two-seater sports car developed and manufactured"
            " in Molsheim, France by French automobile"
            " manufacturer Bugatti Automobiles S.A.S."
            " as the successor to the Bugatti Veyron.",
            category_id=category1.id, user_id=User.id)
session.add(item)
session.commit()

item = Item(name="iPhone XR", description="iPhone XR (stylized as iPhone Xr,"
            " pronounced-ten)is a smartphone designed"
            " and manufactured by Apple, Inc. It is the twelfth"
            " generation of the iPhone.",
            category_id=category2.id, user_id=User.id)
session.add(item)
session.commit()

item = Item(name="COCO NOIR", description="THROUGH BLACK... LIGHT REVEALED has"
            " always entrusted black with an essential role:"
            " to highlight a woman. COCO NOIR an intensely"
            " brilliant fragrance with luminous notes.",
            category_id=category3.id, user_id=User.id)
session.add(item)
session.commit()

item = Item(name="Carolina Herrera", description="Good Girl by Carolina"
            " An audacious blend of dark and light elements.",
            category_id=category3.id, user_id=User.id)
session.add(item)
session.commit()

item = Item(name="South Korea", description="South Korea, officially (ROK),"
            " is a country in East Asia, constituting the southern"
            " part of the Korean Peninsula and lying to the east of"
            " the Asian mainland.",
            category_id=category4.id, user_id=User.id)
session.add(item)
session.commit()

item = Item(name="Hockey", description="Hockey is a sport in which"
            "two teams play against"
            " each other by trying to manoeuvre a ball or a"
            " puck into the opponent's goal using a hockey"
            " stick. There are many types of hockey such"
            " as bandy, field hockey and ice hockey.",
            category_id=category5.id, user_id=User.id)
session.add(item)
session.commit()


print("Database was Populated!")

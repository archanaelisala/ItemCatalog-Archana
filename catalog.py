from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# Load from Gclient_secret.json
CLIENT_ID = json.loads(
                open('Gclient_secret.json', 'r').read()
            )['web']['client_id']

# Define app
app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Retrieve all categories to render them in the templates
categories = session.query(Category).all()


# Landing route
@app.route('/')
def showHome():
    return redirect(url_for('showCatalog'))


# START Authentication routes
@app.route('/login')
def showLogin():
    # Check if user already logged in
    if isLoggedIn():
        flash('You are already logged in!', 'error')
        return redirect(url_for('showCatalog'))

    state = ''.join(random.choice(string.ascii_uppercase + string.
                    digits) for x in xrange(32))

    login_session['state'] = state

    # Pass the state of the user
    return render_template("login.html", STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Check if user already logged in
    if isLoggedIn():
        flash('You are already logged in!', 'error')
        return redirect(url_for('showCatalog'))

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('Gclient_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
                        json.dumps(
                            'Failed to upgrade the authorization code.',
                            401,
                        )
                    )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?'
    url += 'token_type=Bearer&expires_in=604800&access_token=%s' % access_token

    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                json.dumps('Current user is already connected.'), 200
            )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json"
    userinfo_url += "&access_token=%s" % credentials.access_token
    answer = requests.get(userinfo_url)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Check if a user exists
    user_id = getUserID(data['email'])
    if not user_id:
        # Note that this method has access to login_session
        createUser()
    login_session['user_id'] = user_id

    output = '<div class="d-flex mb-3 align-items-center">'
    output += '<h3 class="p-2 display-5">Welcome, '
    output += login_session['username']
    output += '!</h3>'
    output += '<img class="ml-auto p-2" src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px;border-radius: 150px;" '
    output += 'alt"profile image" '
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    output += '</div>'
    flash("you are now logged in as %s" % login_session['username'], "success")
    return output


@app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
    if not isLoggedIn():
        return userNeedsLogin()

    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
                        json.dumps('Current user not connected.'),
                        401
                    )
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke'
    url += '?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # If logging out was successful, remove user from login_session
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        flash('Successfully logged out!', 'success')
        return redirect(url_for('showCatalog'))
    else:
        flash('Could not logout, please try again later.', 'error')
        return redirect(url_for('showCatalog'))
# END authentication routes


# Index  [ Read ]
@app.route('/catalog')
def showCatalog():
    # Get 10 most recent items from Database
    items = session.query(Item).order_by(
                                    Item.created_date.desc()
                                ).limit(10).all()

    return render_template(
                'index.html',
                latestItems=items
            )


@app.route('/catalog/JSON')
def catalogJSON():
    data = {}
    data['categories'] = [i.serialize for i in categories]

    # Retrieve all the categories with their items
    for category in data['categories']:
        items = session.query(Item).filter_by(category_id=category['id'])
        category['items'] = [i.serialize for i in items]
    return jsonify(data)


@app.route('/catalog/<string:category_name>')
def showCategory(category_name):
    try:
        category = session.query(Category).filter_by(name=category_name).one()
    except NoResultFound:
        flash('No category found with that name.', 'error')
        return redirect(url_for('showCatalog'))

    items = session.query(Item).filter_by(category_id=category.id).all()

    return render_template(
            'show_categories.html',
            items=items,
            category_name=category_name,
        )


@app.route('/catalog/<string:category_name>/JSON')
def categoryJSON(category_name):
    # Retrieve category
    try:
        category = session.query(Category).filter_by(name=category_name).one()
    except NoResultFound:
        flash('No category found with that name.', 'error')
        return redirect(url_for('showCatalog'))

    # Retrieve its items
    items = session.query(Item).filter_by(category_id=category.id)

    # Jsonify data
    data = {}
    data['category'] = category.serialize
    data['category']['items'] = [i.serialize for i in items]
    return jsonify(data)


# Add Item  [ Form / Create ]
@app.route('/catalog/add', methods=["GET", "POST"])
def addItem():
    if not isLoggedIn():
        return userNeedsLogin()

    if request.method == "POST":
        addItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            category_id=request.form['category'],
            user_id=login_session['user_id']
        )
        session.add(addItem)
        session.commit()

        flash("Item was successfully added.", "success")
        return redirect(url_for("showCatalog"))

    return render_template('add.html')


# Show Item  [ Read ]
@app.route('/catalog/<string:category>/<int:item_id>')
def showItem(category, item_id):
    try:
        item = session.query(Item).filter_by(id=item_id).one()
    except NoResultFound:
        flash('No item with that ID found.', 'error')
        return redirect(url_for('showCatalog'))

    return render_template('show_items.html', item=item)


# Edit Item  [ Form / Update ]
@app.route('/catalog/<string:category>/<int:item_id>/edit', methods=[
    "GET", "POST"])
def editItem(category, item_id):
    # If user is not logged in, redirect to home page
    if not isLoggedIn():
        return userNeedsLogin()

    try:
        item = session.query(Item).filter_by(id=item_id).one()
    except NoResultFound:
        flash('No item with that ID found.', 'error')
        return redirect(url_for('showCatalog'))

    # If user is not the owner of this item, redirect to home page
    if not isOwner(item.user_id):
        return haveNoPermission()

    if request.method == "POST":
        # Verify user input
        if (request.form['name'] and request.form['description'] and
                request.form['category']):

            item.name = request.form['name']
            item.description = request.form['description']
            item.category_id = request.form['category']

            flash("Item successfully edited.", 'success')
            return redirect(url_for(
                    "showItem",
                    category=item.category.name,
                    item_id=item.id
                )
            )
        else:
            flash("Incorrect item info, please fill it correctly.", "error")
            return redirect(
                        url_for(
                            'editItem',
                            category=category,
                            item_id=item_id
                        )
                    )

    return render_template('edit.html', item=item)


# Delete Item  [ Confirmation / Delete ]
@app.route('/catalog/<string:category>/<int:item_id>/delete', methods=[
    "GET", "POST"])
def deleteItem(category, item_id):
    # If user is not logged in, redirect to home page
    if not isLoggedIn():
        return userNeedsLogin()

    try:
        item = session.query(Item).filter_by(id=item_id).one()
    except NoResultFound:
        flash('No item with that ID found.', 'error')
        return redirect(url_for('showCatalog'))

    if not isOwner(item.user_id):
        return haveNoPermission()

    if request.method == "POST":
        session.delete(item)
        session.commit()
        flash("Successfully deleted item.", "success")
        return redirect(url_for("showCatalog"))

    return render_template('delete.html', item=item)


@app.route('/catalog/<string:category>/<int:item_id>/JSON')
def itemJSON(category, item_id):
    try:
        item = session.query(Item).filter_by(id=item_id).one()
    except NoResultFound:
        flash('No item with that ID found.', 'error')
        return redirect(url_for('showCatalog'))

    data = item.serialize
    return jsonify(data)


# START helper methods
def isLoggedIn():
    return 'username' in login_session


def userNeedsLogin():
    flash('You need to login first!', 'error')
    return redirect(url_for('showLogin'))


def createUser():
    newUser = User(
                name=login_session['username'],
                email=login_session['email'],
                picture=login_session['picture'],
            )
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()

    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except NoResultFound:
        return None


def isOwner(creator_id):
    # Returns True if user was the owner/creator of the item
    return creator_id == login_session['user_id']


def haveNoPermission():
    flash('You do not have permission to do that!', 'error')
    return redirect(url_for('showCatalog'))
# END helper methods


# Pass global variables to all templates
@app.context_processor
def context_processor():
    username = None
    if 'username' in login_session:
        username = login_session['username']

    # categories: a list of categories retrieved from Database.
    # isLoggedIn: a function that checks if user was logged in.
    # isOwner: a function that checks if the user was the owner of a certain
    # item.
    # username: contains the username of the logged in user
    return dict(
        categories=categories,
        isLoggedIn=isLoggedIn,
        isOwner=isOwner,
        username=username
    )


if __name__ == '__main__':
    app.secret_key = 'APP_SECRET_KEY'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

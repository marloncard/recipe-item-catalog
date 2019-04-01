from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import flash
from flask import session as login_session
from flask import make_response
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker, exc
from sqlalchemy.orm.exc import NoResultFound
from models import Base, Category, Recipe, User
import random
import string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
import requests
from functools import wraps

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('/var/www/catalog/client_secrets.json', 'r').read())['web']['client_id']

POSTG_PASS = json.loads(
    open('/var/www/catalog/postgre_pass.json', 'r').read())['password']

# Connect to database and create db session
engine = create_engine('postgresql://catalog:%s@localhost:5432/catalogdb' % POSTG_PASS)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Decorator to redirect user if not logged in and trying to add or modify
# resource.
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in login_session:
            flash('Please Log in')
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper


# Decorator to check if user owns resource they are trying to modify.
def authorized(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        recipe_id = kwargs["recipe_id"]
        recipe = session.query(Recipe).filter_by(id=recipe_id).one()
        if ('user_id' in login_session and
                login_session['user_id'] != recipe.user_id):
            flash("You are not authorized to edit that recipe")
            return render_template('recipe.html',
                                   category_name=kwargs["category_name"],
                                   recipe=recipe)
        return f(*args, **kwargs)
    return wrapper


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already'
                                            'connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 150px; height: 150px;border-radius:'
               '150px;-webkit-border-radius: 150px;-moz-border-radius:'
               '150px;"> ')
    flash("you are now logged in as %s" % login_session['username'])
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
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


# DISCONNECT - Revoke a current user's token and reset their login_session.
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given '
                                            'user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print("access token received %s ") % access_token

    app_id = json.loads(open('/var/www/catalog/fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('/var/www/catalog/fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type='
           'fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token'
           '=%s') % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we
        have to split the token first on commas and select the first index
        which gives us the key : valuefor the server access token then we split
        it on colons to pull out the actual token value and replace the
        remaining quotes with nothing so that it can be used directly in the
        graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = ('https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,'
           'email') % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = ('https://graph.facebook.com/v2.8/me/picture?access_token=%s&'
           'redirect=0&height=200&width=200') % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 100px; height: 100px;border-radius: '
               '150px;-webkit-border-radius: 150px;-moz-border-radius: '
               '150px;"> ')

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
            facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))


# Return JSON data for all recipes in a category
@app.route('/catalog/<string:category_name>/recipes/json')
def showCategoryJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    recipes = session.query(Recipe).filter_by(category_id=category.id).all()
    category = {"Category": category_name,
                "Recipes": [r.serialize for r in recipes]}
    return jsonify(Catalog=category)


# Return JSON data for a specific recipe
@app.route('/catalog/<string:category_name>/recipe/<int:recipe_id>/json')
def showRecipeJSON(category_name, recipe_id):
    recipe = session.query(Recipe).filter_by(id=recipe_id).one()
    return jsonify(Recipe=recipe.serialize)


# Home page of catalog showing latest recipes added in descending order
@app.route('/')
@app.route('/catalog')
def showCatalog():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    latest_recipes = session.query(Recipe).order_by(
        desc(Recipe.id)).limit(10).all()
    print(login_session)
    return render_template(
        'home.html', categories=categories, latest_recipes=latest_recipes)


# Show all recipes in a particular category with sidebar
@app.route('/catalog/<string:category_name>/recipes')
def showCategory(category_name):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    category = session.query(Category).filter_by(name=category_name).one()
    recipes = session.query(Recipe).filter_by(category_id=category.id).all()
    return render_template(
        'recipe-category.html', categories=categories, recipes=recipes,
        category=category)


# Show all recipes in all categories with sidebar
@app.route('/catalog/recipes')
def showRecipes():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    recipes = session.query(Recipe).all()
    return render_template(
        'allrecipes.html', categories=categories, recipes=recipes)


# Show recipe detail
@app.route('/catalog/<string:category_name>/recipe/<int:recipe_id>')
def showRecipe(category_name, recipe_id):
    recipe = session.query(Recipe).filter_by(id=recipe_id).one()
    return render_template(
        'recipe.html', category_name=category_name, recipe=recipe)


# Create a new recipe
@app.route('/catalog/<string:category_name>/recipe/new',
           methods=['GET', 'POST'])
@login_required
def newRecipe(category_name):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    if request.method == 'POST':
        category = session.query(Category).filter_by(
            name=request.form['category']).one()
        newrecipe = Recipe(name=request.form['name'],
                           category_id=category.id,
                           instructions=request.form['instructions'],
                           ingredients=request.form['ingredients'],
                           user_id=login_session['user_id'])
        session.add(newrecipe)
        session.commit()
        flash("New recipe created!")
        return redirect(url_for('showCategory', category_name=category.name))
    else:
        return render_template(
            'newrecipe.html', category_name=category_name,
            categories=categories)


# Edit a recipe
@app.route('/catalog/<string:category_name>/recipe/<int:recipe_id>/edit',
           methods=['GET', 'POST'])
@authorized
@login_required
def editRecipe(category_name, recipe_id):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    editedRecipe = session.query(Recipe).filter_by(id=recipe_id).one()
    if request.method == 'POST':
        category = session.query(Category).filter_by(
            name=request.form['category']).one()
        if request.form['name']:
            editedRecipe.name = request.form['name']
        if request.form['category']:
            editedRecipe.category_id = category.id
        if request.form['instructions']:
            editedRecipe.instructions = request.form['instructions']
        if request.form['ingredients']:
            editedRecipe.ingredients = request.form['ingredients']
        session.add(editedRecipe)
        session.commit()
        flash("Recipe updated!")
        return redirect(url_for('showCategory', category_name=category.name))
    else:
        return render_template(
            'editrecipe.html', category_name=category_name,
            categories=categories, recipe=editedRecipe)


# Delete a recipe
@app.route('/catalog/<string:category_name>/recipe/<int:recipe_id>/delete',
           methods=['GET', 'POST'])
@authorized
@login_required
def deleteRecipe(category_name, recipe_id):
    deletedRecipe = session.query(Recipe).filter_by(id=recipe_id).one()
    if request.method == 'POST':
        session.delete(deletedRecipe)
        session.commit()
        flash("Recipe has been deleted!")
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        return render_template('deleterecipe.html', recipe=deletedRecipe)


# Show the about page
@app.route('/about')
def showAbout():
    return render_template('about.html')


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

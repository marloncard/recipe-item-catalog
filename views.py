from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Recipe, User


app = Flask(__name__)


# Connect to database and create db session
engine = create_engine('sqlite:///recipes.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Home page of catalog showing latest recipes added
@app.route('/')
@app.route('/catalog')
def showCatalog():
    output = ''
    output += '<h1>Hello world!</h1>'
    output += '<p>This page will show categories and latest recipes</p>'
    return output


# Show all recipes in a particular category
@app.route('/catalog/<string:category_name>/recipes')
def showCategory(category_name):
    return "<p>This page will show all recipes in %s category!</p>" % category_name


# Show recipe detail
@app.route('/catalog/<string:category_name>/recipe/<int:recipe_id>')
def showRecipe(category_name, recipe_id):
    return "<p>This page will show the recipe for recipe# %s in %s</p>" % (recipe_id, category_name)


# Create a new recipe
@app.route('/catalog/<string:category_name>/recipe/new')
def newRecipe(category_name):
    return "<p>This is a page to create new recipes</p>"


# Edit a recipe
@app.route('/catalog/<string:category_name>/recipe/<int:recipe_id>/edit')
def editRecipe(category_name, recipe_id):
    return "<p>This page is to edit recipe # %s</p>" % recipe_id


# Delete a recipe
@app.route('/catalog/<string:category_name>/recipe/<int:recipe_id>/delete')
def deleteRecipe(category_name, recipe_id):
    return "<p>This page is to delete recipe # %s" % recipe_id


if __name__ == "__main__":
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

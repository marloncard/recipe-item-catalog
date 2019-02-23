from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Recipe, User


app = Flask(__name__)


# Connect to database and create db session
engine = create_engine('sqlite:///recipes.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Home page of catalog showing latest recipes added in descending order
@app.route('/')
@app.route('/catalog')
def showCatalog():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    latest_recipes = session.query(Recipe).order_by(desc(Recipe.id)).limit(10).all()
    return render_template('home.html', categories=categories, latest_recipes=latest_recipes)


# Show all recipes in a particular category with sidebar
@app.route('/catalog/<string:category_name>/recipes')
def showCategory(category_name):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    category = session.query(Category).filter_by(name=category_name).one()
    recipes = session.query(Recipe).filter_by(category_id=category.id)
    return render_template('recipe-category.html', categories=categories, recipes=recipes, category=category)


# Show recipe detail
@app.route('/catalog/<string:category_name>/recipe/<int:recipe_id>')
def showRecipe(category_name, recipe_id):
    recipe = session.query(Recipe).filter_by(id=recipe_id).one()
    return render_template('recipe.html', category_name=category_name, recipe=recipe)


# Create a new recipe
@app.route('/catalog/<string:category_name>/recipe/new')
def newRecipe(category_name):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    if method == 'POST':
        category = session.query(Category).filter_by(name=request.form['category']).one()
        newrecipe = Recipe(name=request.form['name'],
                           category_id=category.id,
                           instructions=request.form['instructions'],
                           ingredients=request.form['ingredients'],
                           user_id=login_session['user_id'])
    return render_template('newrecipe.html', category_name=category_name, categories=categories)


# Edit a recipe
@app.route('/catalog/<string:category_name>/recipe/<int:recipe_id>/edit')
def editRecipe(category_name, recipe_id):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    if method == 'POST':
        category = session.query(Category).filter_by(name=request.form['category']).one()
        editrecipe = Recipe(name=request.form['name'],
                           category_id=category.id,
                           instructions=request.form['instructions'],
                           ingredients=request.form['ingredients'],
                           user_id=login_session['user_id'])
    return render_template('newrecipe.html', category_name=category_name, categories=categories)


# Delete a recipe
@app.route('/catalog/<string:category_name>/recipe/<int:recipe_id>/delete')
def deleteRecipe(category_name, recipe_id):
    return "<p>This page is to delete recipe # %s" % recipe_id


if __name__ == "__main__":
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

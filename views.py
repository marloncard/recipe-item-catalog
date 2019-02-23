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
@app.route('/catalog/<string:category_name>/recipe/new', methods=['GET', 'POST'])
def newRecipe(category_name):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    if request.method == 'POST':
        category = session.query(Category).filter_by(name=request.form['category']).one()
        newrecipe = Recipe(name=request.form['name'],
                           category_id=category.id,
                           instructions=request.form['instructions'],
                           ingredients=request.form['ingredients'],
                           # user_id=login_session['user_id'])
                           user_id=1) # Temporary - remove after adding auth
        session.add(newrecipe)
        session.commit()
        return redirect(url_for('showCategory', category_name=category.name))
    else:
        return render_template('newrecipe.html', category_name=category_name, categories=categories)


# Edit a recipe
@app.route('/catalog/<string:category_name>/recipe/<int:recipe_id>/edit', methods=['GET', 'POST'])
def editRecipe(category_name, recipe_id):
    categories = session.query(Category).order_by(asc(Category.name)).all()
    editedRecipe = session.query(Recipe).filter_by(id=recipe_id).one()
    if request.method == 'POST':
        category = session.query(Category).filter_by(name=request.form['category']).one()
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
        return redirect(url_for('showCategory', category_name=category.name))
    else:
        return render_template('editrecipe.html', category_name=category_name, categories=categories, recipe=editedRecipe)


# Delete a recipe
@app.route('/catalog/<string:category_name>/recipe/<int:recipe_id>/delete', methods=['GET', 'POST'])
def deleteRecipe(category_name, recipe_id):
    deletedRecipe = session.query(Recipe).filter_by(id=recipe_id).one()
    if request.method == 'POST':
        session.delete(deletedRecipe)
        session.commit()
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        return render_template('deleterecipe.html', recipe=deletedRecipe)


if __name__ == "__main__":
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

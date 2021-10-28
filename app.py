import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def index():
    top_recipes = mongo.db.recipes.find().sort("user_favourite")[:3]
    return render_template('index.html', top_recipes=top_recipes)


@app.route("/recipes")
def recipes():
    recipes = list(mongo.db.recipes.find())
    return render_template("recipes.html", recipes=recipes)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "email": request.form.get("email").lower(),
            "user_recipes": [],
            "saved_recipes": [],
            "admin": False,
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                session["admin"] = mongo.db.users.find_one(
                    {"username": session["user"]})["admin"]
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    # grab the recipes from the db
    recipes = list(mongo.db.recipes.find())
    if session["user"]:
        return render_template(
            "profile.html", username=username, recipes=recipes)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    session.pop("admin")
    return redirect(url_for("login"))


@app.route("/admin")
def admin():
    return render_template('admin.html')


ingredients = []


# @app.route("/add_ingredient", methods=['GET', 'POST'])
# def add_ingredient():
#     items = request.form.get("item").readlines()
#     quantities = request.form.get("quantity")
#     print(items)
#     print(quantities)
#     return render_template("add_recipe.html")


@app.route("/add_recipe", methods=['GET', 'POST'])
def add_recipe():
    if request.method == "POST":
        ingredient_list = request.form.getlist("ingredients")
        preparation_list = request.form.getlist("ingredient-prep")
        ingredients = []
        ingredient = {"item": "", "preparation": ""}
        for i, p in zip(ingredient_list, preparation_list):
            ingredient["item"] = i
            ingredient["preparation"] = p
            ingredient_copy = ingredient.copy()
            ingredients.append(ingredient_copy)

        recipe = {
            "recipe_name": request.form.get("recipe_name"),
            "recipe_chef": request.form.get("recipe_chef"),
            "recipe_image": request.form.get("recipe_image"),
            "recipe_summary": request.form.get("recipe_summary"),
            "prep_time": request.form.get("prep_time"),
            "cook_time": request.form.get("cook_time"),
            "ingredients": ingredients,
            "method": request.form.getlist("method"),
            "vegetarian": request.form.get("vegetarian"),
            "vegan": request.form.get("vegan"),
            "uploaded_by": session["user"],
            "recipe_made_count": [],
            "user_favourite": []
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe Successfully Added")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("add_recipe.html")


@app.route("/edit_recipe/<recipe_id>", methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    if request.method == "POST":
        ingredient_list = request.form.getlist("ingredients")
        preparation_list = request.form.getlist("ingredient-prep")
        ingredients = []
        ingredient = {"item": "", "preparation": ""}
        for i, p in zip(ingredient_list, preparation_list):
            ingredient["item"] = i
            ingredient["preparation"] = p
            ingredient_copy = ingredient.copy()
            ingredients.append(ingredient_copy)

        update = {
            "recipe_name": request.form.get("recipe_name"),
            "recipe_chef": request.form.get("recipe_chef"),
            "recipe_image": request.form.get("recipe_image"),
            "recipe_summary": request.form.get("recipe_summary"),
            "prep_time": request.form.get("prep_time"),
            "cook_time": request.form.get("cook_time"),
            "ingredients": ingredients,
            "method": request.form.getlist("method"),
            "vegetarian": request.form.get("vegetarian"),
            "vegan": request.form.get("vegan"),
            "uploaded_by": session["user"],
            "recipe_made_count": recipe["recipe_made_count"],
            "user_favourite": recipe["user_favourite"]
        }
        mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, update)
        flash("Recipe Successfully Updated")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("edit_recipe.html", recipe=recipe)


@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("Recipe Successfully Deleted")
    return redirect(url_for("profile", username=session["user"]))


@app.route("/recipe_favourite/<recipe_id>")
def recipe_favourite(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    if session["user"] in recipe["user_favourite"]:
        mongo.db.recipes.update({"_id": ObjectId(
            recipe_id)}, {"$pull": {"user_favourite": session["user"]}})
        mongo.db.users.update({"username": session["user"]}, {
            "$pull": {"favourite_recipes": recipe["_id"]}})
    else:
        mongo.db.recipes.update({"_id": ObjectId(
            recipe_id)}, {"$push": {"user_favourite": session["user"]}})
        mongo.db.users.update({"username": session["user"]}, {
            "$push": {"favourite_recipes": recipe["_id"]}})
    return redirect(url_for("recipe_ingredients", recipe_id=recipe["_id"]))


@app.route("/recipe_ingredients/<recipe_id>", methods=["GET", "POST"])
def recipe_ingredients(recipe_id):
    if "user" in session:
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        return render_template("recipe_ingredients.html", recipe=recipe)
    else:
        flash("Please login or register to view recipe")
        return redirect(url_for("login"))


@app.route("/recipe_method/<recipe_id>", methods=["GET", "POST"])
def recipe_method(recipe_id):
    if "user" in session:
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        return render_template("recipe_method.html", recipe=recipe)
    else:
        flash("Please login or register to view recipe")
        return redirect(url_for("login"))


@app.route("/recipe_made/<recipe_id>", methods=["GET", "POST"])
def recipe_made(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    stamp = datetime.datetime.utcnow()
    recipe_made_count = recipe["recipe_made_count"]
    if session["user"] in recipe_made_count["user"].values() and recipe_made_count["time"] > stamp - 24*60*60 * 1000:
        mongo.db.recipes.update({"_id": ObjectId(
                recipe_id)}, {"$push": {"recipe_made_count": {
                    "user": session["user"], "time": stamp}}})
    else:
        print("too soon")
    return redirect(url_for("recipe_ingredients", recipe_id=recipe["_id"]))


def print_test():
    print('Hello, World!')


print_test()


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

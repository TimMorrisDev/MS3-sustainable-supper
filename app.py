import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
# from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def index():
    return render_template('index.html')


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
                # session["userId"] = mongo.db.users.find_one(
                #     {"username": session["user"]}[str(ObjectId())])
                # session["userId"] = ObjectId(mongo.db.users.find_one(
                #     {"username": session["user"]})["_id"])
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
        return render_template("profile.html", username=username, recipes=recipes)

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
        recipe = {
            "recipe_name": request.form.get("recipe_name"),
            "recipe_chef": request.form.get("recipe_chef"),
            "recipe_image": request.form.get("recipe_image"),
            "recipe_summary": request.form.get("recipe_summary"),
            "prep_time": request.form.get("prep_time"),
            "cook_time": request.form.get("cook_time"),
            "ingredients": request.form.getlist("ingredients"),
            "method": request.form.getlist("method"),
            "vegetarian": request.form.get("vegetarian"),
            "vegan": request.form.get("vegan"),
            "uploaded_by": session["user"],
            "recipe_made_count": 0,
            "user_favourite": []
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe Successfully Added")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("add_recipe.html")


@app.route("/edit_recipe/<recipe_id>", methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    if request.method == "POST":
        update = {
            "recipe_name": request.form.get("recipe_name"),
            "recipe_chef": request.form.get("recipe_chef"),
            "recipe_image": request.form.get("recipe_image"),
            "recipe_summary": request.form.get("recipe_summary"),
            "prep_time": request.form.get("prep_time"),
            "cook_time": request.form.get("cook_time"),
            "ingredients": request.form.getlist("ingredients"),
            "method": request.form.getlist("method"),
            "vegetarian": request.form.get("vegetarian"),
            "vegan": request.form.get("vegan"),
            "uploaded_by": session["user"],
            "recipe_made_count": 0,
            "user_favourite": []
        }
        mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, update)
        flash("Recipe Successfully Updated")
        return redirect(url_for("profile", username=session["user"]))
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("edit_recipe.html", recipe=recipe)


@app.route("/recipe_ingredients/<recipe_id>", methods=["GET", "POST"])
def recipe_ingredients(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("recipe_ingredients.html", recipe=recipe)


@app.route("/recipe_method/<recipe_id>", methods=["GET", "POST"])
def recipe_method(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("recipe_method.html", recipe=recipe)


def print_test():
    print('Hello, World!')


print_test()


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

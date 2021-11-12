import os
from datetime import datetime, timedelta
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo, pymongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# landing page and top 3 recipes
@app.route("/")
@app.route("/index")
def index():

    # get top 3 recipes based on amount of user favourites
    top_recipes = mongo.db.recipes.find().sort(
        "user_favourite", pymongo.DESCENDING).limit(3)

    # get top 3 recipes based on count of 'I made this' button
    most_made = mongo.db.recipes.find().sort(
        "recipe_made_count", pymongo.DESCENDING).limit(3)
    return render_template(
        'index.html', top_recipes=top_recipes, most_made=most_made)


# search function
@app.route("/search", methods=["GET", "POST"])
def search():

    # get search input from form
    query = request.form.get("query")

    # return matching recipes from db
    result_recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    return render_template("recipes.html", recipes=result_recipes)


# pantry search funciton
@app.route("/pantry_search/<username>", methods=["GET", "POST"])
def pantry_search(username):

    # get search input from db field 'user_ingredients"
    query = mongo.db.users.find_one(
        {"username": username})["user_ingredients"]

    # check if user has items in thier pantry
    if query:
        # return matching recipes from db
        result_recipes = list(mongo.db.recipes.find({
            "$text": {"$search": str(query)}}))
        return render_template("recipes.html", recipes=result_recipes)

    # prompt user to update pantry if list returns empty
    else:
        flash("Your pantry is empty! Update it to view matches")
        return redirect(url_for("profile", username=username))


# recipes page
@app.route("/recipes")
def recipes():

    # check if user is logged in
    if "user" in session:

        # get all recipes from db
        recipes = list(mongo.db.recipes.find())
        return render_template("recipes.html", recipes=recipes)
    else:

        # prompt login or signup if no user signed in
        flash("Please login or register to view recipes")
        return redirect(url_for("login"))


# USER FUNCTIONS

class EntryForm(FlaskForm):
    username = StringField('username', validators=[InputRequired('Please enter your username')])
    password = PasswordField('password', validators=[InputRequired('Please enter your password')])


# register new user function
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
            "user_recipes": [],
            "favourite_recipes": [],
            "admin": False,
            "user_ingredients": []

        }
        # add user to the db
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()

        # put admin status into session cookie
        session["admin"] = False

        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


# login function
@app.route("/login", methods=["GET", "POST"])
def login():
    form = EntryForm()
    if request.method == "POST":

        if form.validate_on_submit():
            # check if username already exists in db
            existing_user = mongo.db.users.find_one(
                {"username": request.form.get("username").lower()})

            if existing_user:

                # ensure hashed password matches user input
                if check_password_hash(
                        existing_user["password"], request.form.get("password")):

                    # add username to session cookie
                    session["user"] = request.form.get("username").lower()

                    # add admin status for user to session cookie
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
        else:
            error_values = form.errors.values()
            for v in error_values:
                flash(v[0])
            
    return render_template("login.html", form=form)


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):

    # fetch the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    # fetch the  user's pantry ingredients from db
    user_ingredients = mongo.db.users.find_one(
        {"username": session["user"]})["user_ingredients"]

    # fetch the user's favourite recipes from db
    favourite_recipes = mongo.db.users.find_one(
        {"username": session["user"]})["favourite_recipes"]

    # grab the recipes from the db
    recipes = list(mongo.db.recipes.find())
    if session["user"]:
        return render_template(
            "profile.html", username=username, recipes=recipes,
            user_ingredients=user_ingredients,
            favourite_recipes=favourite_recipes)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():

    # remove user from session cookies
    session.pop("user")

    # check if user is admin
    if session["admin"]:
        session.pop("admin")

    flash("You have been logged out")
    return redirect(url_for("login"))


@app.route("/delete_user/<username>")
def delete_user(username):
    # find user to delete
    user = mongo.db.users.find_one(
        {"username": username})

    # remove user from session cookies
    session.pop("user")

    # check if user is admin
    if session["admin"]:
        session.pop("admin")

    # remove user from recipe favourite field in db
    recipes = list(mongo.db.recipes.find())
    for recipe in recipes:
        if user["username"] in recipe["user_favourite"]:
            mongo.db.recipes.update(recipe, {
                "$pull": {"user_favourite": user["username"]}})

        # re-assign any recipes made by user to admin
        # to prevent future registrations having edit access
        if user["username"] == recipe["uploaded_by"]:
            mongo.db.recipes.update(recipe, {"$set": {"uploaded_by": "admin"}})

    # remove user from db
    mongo.db.users.delete_one(user)
    flash("User profile deleted")
    return redirect(url_for("index"))


# function to navigate to admin section of site
@app.route("/admin")
def admin():
    # get all recipes from db
    recipes = list(mongo.db.recipes.find())

    # get all users from db
    users = list(mongo.db.users.find())
    return render_template('admin.html', users=users, recipes=recipes)


@app.route("/admin_delete_user/<username>")
def admin_delete_user(username):
    # find user to delete
    user = mongo.db.users.find_one(
        {"username": username})

    # remove user from db
    mongo.db.users.delete_one(user)
    flash("User profile deleted")
    return redirect(url_for("admin"))


# function for admin to change other user status
@app.route("/admin_status/<username>")
def admin_status(username):

    # locate user in db
    user = mongo.db.users.find_one(
        {"username": username})

    # store admin status in variable
    admin = mongo.db.users.find_one(
                    {"username": username})["admin"]

    # check for user admin status
    if not admin:
        # set as admin if not
        mongo.db.users.update(user, {
            "$set": {"admin": True}})
        flash("User admin status granted")
    else:
        # remove admin status if already admin
        mongo.db.users.update(user, {
            "$set": {"admin": False}})
        flash("User admin status removed")
    return redirect(url_for("admin"))


# function to update user pantry ingredients
@app.route("/update_ingredients/<username>", methods=["GET", "POST"])
def update_ingredients(username):
    if request.method == "POST":

        # get list of ingredients from update form
        ingredients = request.form.getlist("user-ingredients")

        # update the existing db field
        mongo.db.users.update({"username": username}, {
            "$set": {"user_ingredients": ingredients}})
        return redirect(url_for("profile", username=username))
    return redirect(url_for("profile", username=username))


# function to add user recipe
@app.route("/add_recipe", methods=['GET', 'POST'])
def add_recipe():

    # collect data to populate new dictionary object
    if request.method == "POST":

        # build ingredient dict by iterating through two form lists
        ingredient_list = request.form.getlist("ingredients")
        preparation_list = request.form.getlist("ingredient-prep")
        ingredients = []
        ingredient = {"item": "", "preparation": ""}
        for i, p in zip(ingredient_list, preparation_list):

            # loop through two lists and append ingredients variable
            ingredient["item"] = i
            ingredient["preparation"] = p
            ingredient_copy = ingredient.copy()
            ingredients.append(ingredient_copy)

        # build recipe object to add to database
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
            "date_added": datetime.now(),
            "recipe_made_count": [],
            "user_favourite": []
        }
        # append to db
        mongo.db.recipes.insert_one(recipe)

        # get newly added recipe from db by sorting using date_added field
        new_recipe = mongo.db.recipes.find().sort("date_added", -1).limit(1)

        # store collection result to list for iteration
        i = []
        for recipe in new_recipe:
            i.append(recipe)

        # add new recipe id to user db entry
        mongo.db.users.update({"username": session["user"]}, {
                "$push": {"user_recipes": ObjectId(i[0]["_id"])}})

        flash("Recipe Successfully Added")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("add_recipe.html")


# edit user recipe function
@app.route("/edit_recipe/<recipe_id>", methods=['GET', 'POST'])
def edit_recipe(recipe_id):

    # retreive recipe from db
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    if request.method == "POST":

        # build ingredient dict by iterating through two form lists
        ingredient_list = request.form.getlist("ingredients")
        preparation_list = request.form.getlist("ingredient-prep")
        ingredients = []
        ingredient = {"item": "", "preparation": ""}
        for i, p in zip(ingredient_list, preparation_list):

            # loop through two lists and append ingredients variable
            ingredient["item"] = i
            ingredient["preparation"] = p
            ingredient_copy = ingredient.copy()
            ingredients.append(ingredient_copy)

        # build recipe update object to add to database
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
        # update db entry
        mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, update)
        flash("Recipe Successfully Updated")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("edit_recipe.html", recipe=recipe)


# delete recipe function
@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):

    # remove recipe from user favourite recipes field in db
    users = list(mongo.db.users.find())
    for user in users:
        if ObjectId(recipe_id) in user["favourite_recipes"]:
            mongo.db.users.update(user, {
                "$pull": {"favourite_recipes": ObjectId(recipe_id)}})

    # remove database entry using objectId passed from site
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("Recipe Successfully Deleted")
    return redirect(url_for("profile", username=session["user"]))


# view selected recipe ingredients
@app.route("/recipe_ingredients/<recipe_id>", methods=["GET", "POST"])
def recipe_ingredients(recipe_id):
    # check if user is logged in
    if "user" in session:

        # fetch the selected recipe from db to send for jinja templating
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        return render_template("recipe_ingredients.html", recipe=recipe)
    else:
        flash("Please login or register to view recipe")
        return redirect(url_for("login"))


# view selected recipe method
@app.route("/recipe_method/<recipe_id>", methods=["GET", "POST"])
def recipe_method(recipe_id):
    # check if user is logged in
    if "user" in session:

        # fetch the selected recipe from db to send for jinja templating
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        return render_template("recipe_method.html", recipe=recipe)
    else:
        flash("Please login or register to view recipe")
        return redirect(url_for("login"))


# add recipe to user favourite function
@app.route("/recipe_favourite/<recipe_id>")
def recipe_favourite(recipe_id):

    # fetch db entry
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})

    # check if already a user favourite
    if session["user"] in recipe["user_favourite"]:

        # update db to remove username from recipe document
        mongo.db.recipes.update({"_id": ObjectId(
            recipe_id)}, {"$pull": {"user_favourite": session["user"]}})

        # update db to remove recipe id from user document
        mongo.db.users.update({"username": session["user"]}, {
            "$pull": {"favourite_recipes": recipe["_id"]}})
    else:
        # update db to add username from recipe document
        mongo.db.recipes.update({"_id": ObjectId(
            recipe_id)}, {"$push": {"user_favourite": session["user"]}})

        # update db to add recipe id from user document
        mongo.db.users.update({"username": session["user"]}, {
            "$push": {"favourite_recipes": recipe["_id"]}})
    return redirect(url_for("recipe_ingredients", recipe_id=recipe["_id"]))


# function to log when a user makes a recipe
@app.route("/recipe_made/<recipe_id>", methods=["GET", "POST"])
def recipe_made(recipe_id):

    # fetch the selected recipe from db
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})

    # create datetime variables for use determining when user last made recipe
    now = datetime.now()
    delta = timedelta(days=1)
    past = now-delta

    # fetch db field to be updated
    recipe_made_count = recipe["recipe_made_count"]

    # iterate through db field to find if user has made the recipe within the
    # last day and if they have, add to list
    recipe_made_users = [u.items() for u in recipe_made_count if u[
        "user"] == session["user"] and u["time"] > past]

    # add user and current time to db if created list is empty
    if not recipe_made_users:
        mongo.db.recipes.update({"_id": ObjectId(
                recipe_id)}, {"$push": {"recipe_made_count": {
                    "user": session["user"], "time": now}}})
        flash("Enjoy your meal!")
    else:
        flash("Sorry, you already recorded making this today")
        # mongo.db.recipes.update({"_id": ObjectId(
        #         recipe_id)}, {"$push": {"recipe_made_count": {
        #             "user": session["user"], "time": now}}})
    return redirect(url_for("recipe_ingredients", recipe_id=recipe["_id"]))


# def sort_test():
#     sorted_recipes = mongo.db.recipes.find().sort("date_added", -1).limit(1)
#     x = []
#     for recipe in sorted_recipes:
#         x.append(recipe)
#     print(x)
#     print(x[0]["_id"])


# sort_test()


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

import os
from datetime import datetime, timedelta
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo, pymongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Regexp, Length, URL
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import requests
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
        "favourite_count", pymongo.DESCENDING).limit(3)

    # get top 3 recipes based on count of 'I made this' button
    most_made = mongo.db.recipes.find().sort(
        "made_count", pymongo.DESCENDING).limit(3)
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

    # check if user is logged in
    if "user" in session:

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
    else:
        # redirect if no user logged in
        flash("Please login or register to access this")
        return redirect(url_for("login"))


# recipes page
@app.route("/recipes")
def recipes():

    # get all recipes from db
    recipes = list(mongo.db.recipes.find())
    return render_template("recipes.html", recipes=recipes)


# USER FUNCTIONS

# wtforms validation
class EntryForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(
        'Please enter valid username')])
    password = PasswordField('password', validators=[InputRequired(
        'Please enter valid password')])


# register new user function
@app.route("/register", methods=["GET", "POST"])
def register():

    # store validation parameters
    form = EntryForm()

    if request.method == "POST":

        # check user input passes wtf validation
        if form.validate_on_submit():

            # check if username already exists in db
            existing_user = mongo.db.users.find_one(
                {"username": request.form.get("username").lower()})

            if existing_user:
                flash("Username already exists")
                return redirect(url_for("register"))

            register = {
                "username": request.form.get("username").lower(),
                "password": generate_password_hash(request.form.get(
                    "password")),
                "user_recipes": [],
                "favourite_recipes": [],
                "admin": False,
                "super_admin": False,
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
        else:
            # store any wtf validation errors in variable
            error_values = form.errors.values()

            # iterate through errors and display to user
            for v in error_values:
                flash(v[0])

    return render_template("register.html", form=form)


# login function
@app.route("/login", methods=["GET", "POST"])
def login():
    # store validation parameters
    form = EntryForm()

    if request.method == "POST":

        # check user input passes wtf validation
        if form.validate_on_submit():

            # check if username already exists in db
            existing_user = mongo.db.users.find_one(
                {"username": request.form.get("username").lower()})

            if existing_user:

                # ensure hashed password matches user input
                if check_password_hash(
                        existing_user["password"], request.form.get(
                            "password")):

                    # add username to session cookie
                    session["user"] = request.form.get("username").lower()

                    # add admin status for user to session cookie
                    session["admin"] = mongo.db.users.find_one(
                        {"username": session["user"]})["admin"]
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))
                else:
                    # invalid password match
                    flash("Incorrect Username and/or Password")
                    return redirect(url_for("login"))

            else:
                # username doesn't exist
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))
        else:
            # store any wtf validation errors in variable
            error_values = form.errors.values()

            # iterate through errors and display to user
            for v in error_values:
                flash(v[0])

    return render_template("login.html", form=form)


# user profile page
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):

    # grab the recipes from the db
    recipes = list(mongo.db.recipes.find())

    # fetch the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    # fetch the  user's pantry ingredients from db
    user_ingredients = mongo.db.users.find_one(
        {"username": session["user"]})["user_ingredients"]

    # check if user is logged in
    if session["user"]:
        return render_template(
            "profile.html", username=username, recipes=recipes,
            user_ingredients=user_ingredients)

    # redirect if no user logged in
    return redirect(url_for("login"))


# user logout function
@app.route("/logout")
def logout():

    # remove user from session cookies
    session.pop("user")

    # check if user is admin
    if session["admin"]:
        session.pop("admin")

    flash("You have been logged out")
    return redirect(url_for("login"))


# delete user profile
@app.route("/delete_user/<username>")
def delete_user(username):

    # check if user is logged in
    if "user" in session:

        # find user to delete
        user = mongo.db.users.find_one(
            {"username": username})

        # remove user from session cookies
        session.pop("user")

        # check if user is admin
        if session["admin"]:
            session.pop("admin")

        # remove user from recipe favourite field in db
        # decrease favourite count of matching recipes by 1
        recipes = list(mongo.db.recipes.find())
        for recipe in recipes:
            if user["username"] in recipe["user_favourite"]:
                mongo.db.recipes.update(recipe, {
                    "$pull": {"user_favourite": user["username"]},
                    "$inc": {"favourite_count": -1}
                    })

            # re-assign any recipes made by user to admin
            # to prevent future registrations having edit access
            if user["username"] == recipe["uploaded_by"]:
                # mongo.db.recipes.update(recipe, {
                #     "$set": {"uploaded_by": "admin"}})
                mongo.db.recipes.delete_one(recipe)

        # remove user from db
        mongo.db.users.delete_one(user)
        flash("User profile deleted")
        return redirect(url_for("index"))
    else:
        # redirect if user not logged in
        flash('You do not have permission to do this')
        return redirect(url_for("index"))


# USER PROFILE FUNCTIONS

# function to update user pantry ingredients
@app.route("/update_ingredients/<username>", methods=["GET", "POST"])
def update_ingredients(username):

    # check if user is logged in
    if "user" in session:

        if request.method == "POST":

            # get list of ingredients from update form
            ingredients = request.form.getlist("user-ingredients")

            # update the existing db field
            mongo.db.users.update({"username": username}, {
                "$set": {"user_ingredients": ingredients}})
            return redirect(url_for("profile", username=username))
        return redirect(url_for("profile", username=username))
    else:
        # redirect if no user logged in
        flash("Please login or register to view recipe")
        return redirect(url_for("login"))


# wtforms validation for recipe add /edit
class RecipeForm(FlaskForm):
    # recipe name
    recipe_name = StringField('recipe_name', validators=[
        InputRequired('Please enter recipe name'),
        Length(min=2, max=100, message='''Recipe name must be
                between 2 and 100 characters''')
    ])
    # recipe chef
    recipe_chef = StringField('recipe_chef', validators=[
        InputRequired('Please enter recipe chef'),
        Length(2, 100, 'Chef name must be between 2 and 100 characters')
    ])
    # recipe image
    recipe_image = StringField('recipe_image', validators=[
        InputRequired('Please enter an image URL'),
        URL(require_tld=True, message='Invalid image url')
    ])
    # recipe summary
    recipe_summary = StringField('recipe_summary', validators=[
        InputRequired('Please enter a recipe summary'),
        Length(2, 200, 'Summary must be between 2 and 200 characters')
    ])
    # prep time
    prep_time = StringField('prep_time', validators=[
        InputRequired('Please enter prep time'),
        Regexp('[0-9]', 0, 'Numbers only for prep time'),
        Length(1, 5, 'Prep time must be between 1 and 5 characters')
    ])
    # cook time
    cook_time = StringField('cook_time', validators=[
        InputRequired('Please enter cook time'),
        Regexp('[0-9]', 0, 'Numbers only for cook time'),
        Length(1, 5, 'Cook time must be between 1 and 5 characters')
    ])
    # ingredients
    ingredients = StringField('ingredients', validators=[
        InputRequired('Please enter an ingredient')
    ])
    # method
    method = StringField('ingredients', validators=[
        InputRequired('Please enter an ingredient')
    ])


# function to add user recipe
@app.route("/add_recipe", methods=['GET', 'POST'])
def add_recipe():

    # check if user is logged in
    if "user" in session:

        # store validation parameters
        form = RecipeForm()

        # check user input passes wtf validation
        if form.validate_on_submit():

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

                # check recipe image url for valid image file
                recipe_image = ""
                image_formats = ("image/png", "image/jpeg", "image/jpg")
                image_url = request.form.get("recipe_image")
                r = requests.head(image_url)

                # check if image at url is valid format
                if r.headers["content-type"] in image_formats:
                    recipe_image = image_url
                    print("it's an image")
                else:
                    # provide default image if no valid image found
                    recipe_image = "https://static.onecms.io/wp-content/uploads/sites/44/2021/02/04/watercress-salad-honey-Balsamic-tofu-2000.jpg"
                    flash("Image not valid, default image applied")

                # build recipe object to add to database
                recipe = {
                    "recipe_name": request.form.get("recipe_name"),
                    "recipe_chef": request.form.get("recipe_chef"),
                    "recipe_image": recipe_image,
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
                    "user_favourite": [],
                    "made_count": 0,
                    "favourite_count": 0
                }
                # append to db
                insert = mongo.db.recipes.insert_one(recipe)

                # add new recipe id to user db entry using returned id value
                mongo.db.users.update_one({
                    "username": session["user"]}, {
                        "$push": {
                            "user_recipes": ObjectId(insert.inserted_id)}})

                flash("Recipe Successfully Added")
                return redirect(url_for("profile", username=session["user"]))
        else:
            # store any wtf validation errors in variable
            error_values = form.errors.values()

            # iterate through errors and display to user
            for v in error_values:
                flash(v[0])

        return render_template("add_recipe.html", form=form)
    else:
        # redirect if no user logged in
        flash("Please login or register to view recipe")
        return redirect(url_for("login"))


# edit user recipe function
@app.route("/edit_recipe/<recipe_id>", methods=['GET', 'POST'])
def edit_recipe(recipe_id):

    # store validation parameters
    form = RecipeForm()

    # retreive recipe from db
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})

    # check that recipe was uploaded by user
    if recipe["uploaded_by"] == session["user"]:

        # check user input passes wtf validation
        if form.validate_on_submit():

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

                # check recipe image url for valid image file
                recipe_image = ""
                image_formats = ("image/png", "image/jpeg", "image/jpg")
                image_url = request.form.get("recipe_image")
                r = requests.head(image_url)

                # check if image at url is valid format
                if r.headers["content-type"] in image_formats:
                    recipe_image = image_url
                    print("it's an image")
                else:
                    # provide default image if no valid image found
                    recipe_image = "https://static.onecms.io/wp-content/uploads/sites/44/2021/02/04/watercress-salad-honey-Balsamic-tofu-2000.jpg"
                    flash("Image not valid, default image applied")

                # build recipe update object to add to database
                update = {
                    "recipe_name": request.form.get("recipe_name"),
                    "recipe_chef": request.form.get("recipe_chef"),
                    "recipe_image": recipe_image,
                    "recipe_summary": request.form.get("recipe_summary"),
                    "prep_time": request.form.get("prep_time"),
                    "cook_time": request.form.get("cook_time"),
                    "ingredients": ingredients,
                    "method": request.form.getlist("method"),
                    "vegetarian": request.form.get("vegetarian"),
                    "vegan": request.form.get("vegan"),
                    "uploaded_by": session["user"],
                    "recipe_made_count": recipe["recipe_made_count"],
                    "user_favourite": recipe["user_favourite"],
                    "made_count": recipe["made_count"],
                    "favourite_count": recipe["favourite_count"]

                }
                # update db entry
                mongo.db.recipes.update_one({
                    "_id": ObjectId(recipe_id)}, {"$set": update})
                flash("Recipe Successfully Updated")
                return redirect(url_for("profile", username=session["user"]))
        else:
            # store any wtf validation errors in variable
            error_values = form.errors.values()

            # iterate through errors and display to user
            for v in error_values:
                flash(v[0])
    else:
        # redirect if user did not upload recipe
        flash('You do have permission to do this')
        return redirect(url_for("index"))
    return render_template("edit_recipe.html", recipe=recipe, form=form)


# delete recipe function
@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):

    # retreive recipe from db
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})

    # get user from db
    user = mongo.db.users.find_one({"username": session["user"]})

    # check that recipe was uploaded by user
    if recipe["uploaded_by"] == session["user"]:

        # remove recipe from user uploaded recipes field in db
        mongo.db.users.update_one(user, {"$pull": {
            "user_recipes": ObjectId(recipe_id)}})

        # remove recipe from user favourite recipes field in db
        # users = list(mongo.db.users.find())
        # for u in users:
        #     if ObjectId(recipe_id) in u["favourite_recipes"]:
        #         mongo.db.users.update(u, {
        #             "$pull": {"favourite_recipes": ObjectId(recipe_id)}})

        # remove database entry using objectId passed from site
        mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
        flash("Recipe Successfully Deleted")
        return redirect(url_for("profile", username=session["user"]))
    else:
        # redirect if user did not upload recipe
        flash('You do have permission to do this')
        return redirect(url_for("index"))


# RECIPE DETAIL FUNCTIONS

# view selected recipe ingredients
@app.route("/recipe_ingredients/<recipe_id>", methods=["GET", "POST"])
def recipe_ingredients(recipe_id):

    # fetch the selected recipe from db to send for jinja templating
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("recipe_ingredients.html", recipe=recipe)


# add recipe to user favourite function
@app.route("/recipe_favourite/<recipe_id>")
def recipe_favourite(recipe_id):

    # check if a user is logged in
    if "user" in session:

        # fetch db entry
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})

        # check if already a user favourite
        if session["user"] in recipe["user_favourite"]:

            # update db to remove username from recipe document 
            # and decrease favourite count by 1
            mongo.db.recipes.update({"_id": ObjectId(
                recipe_id)}, {
                    "$pull": {"user_favourite": session["user"]},
                    "$inc": {"favourite_count": -1}
                    })
        else:
            # update db to add username from recipe document
            # and increace favourite count by 1
            mongo.db.recipes.update({"_id": ObjectId(
                recipe_id)}, {
                    "$push": {"user_favourite": session["user"]},
                    "$inc": {"favourite_count": 1}
                    })

        # update db to add recipe id from user document
        # mongo.db.users.update({"username": session["user"]}, {
        #     "$push": {"favourite_recipes": recipe["_id"]}})
        return redirect(url_for("recipe_ingredients", recipe_id=recipe["_id"]))
    else:
        # redirect if no user logged in
        flash("Please login or register to add favourite")
        return redirect(url_for("login"))


# function to log when a user makes a recipe
@app.route("/recipe_made/<recipe_id>", methods=["GET", "POST"])
def recipe_made(recipe_id):

    # check if a user is logged in
    if "user" in session:

        # fetch the selected recipe from db
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})

        # create datetime variables
        # for use determining when user last made recipe
        now = datetime.now()
        delta = timedelta(days=1)
        past = now-delta

        # fetch db field to be updated
        recipe_made_count = recipe["recipe_made_count"]

        # iterate through db field
        # find if user has made the recipe within the last day
        # if they have, add to list
        recipe_made_users = [u.items() for u in recipe_made_count if u[
            "user"] == session["user"] and u["time"] > past]

        # add user and current time to db if created list is empty
        if not recipe_made_users:
            mongo.db.recipes.update({"_id": ObjectId(
                    recipe_id)}, {"$push": {"recipe_made_count": {
                        "user": session["user"], "time": now}}})
            flash("Enjoy your meal!")
        else:
            # display error is user already made in the last day
            flash("Sorry, you already recorded making this today")

        return redirect(url_for("recipe_ingredients", recipe_id=recipe["_id"]))
    else:
        # redirect if no user logged in
        flash("Please login or register to log your meal")
        return redirect(url_for("login"))


# ADMIN FUNCTIONS

# function to navigate to admin section of site
@app.route("/admin")
def admin():

    # check if user is logged in
    if "user" in session:

        # get user admin status from db
        admin = mongo.db.users.find_one(
            {"username": session["user"]})["admin"]
        
        super_admin = mongo.db.users.find_one(
            {"username": session["user"]})["super_admin"]

        if admin:

            # get all recipes from db
            recipes = list(mongo.db.recipes.find())

            # get all users from db
            users = list(mongo.db.users.find())
            return render_template(
                'admin.html', users=users, recipes=recipes,
                super_admin=super_admin)
        else:
            # redirect if not admin
            flash("Please login as admin to view this page")
            return redirect(url_for("index"))
    else:
        # redirect if no user logged in
        flash("Please login as admin to view this page")
        return redirect(url_for("index"))


@app.route("/admin_delete_user/<username>")
def admin_delete_user(username):

    # check if user is logged in
    if "user" in session:

        # get user admin status from db
        admin = mongo.db.users.find_one(
            {"username": session["user"]})["admin"]

        if admin:
            # find user to delete
            user = mongo.db.users.find_one(
                {"username": username})

            # remove user from db
            mongo.db.users.delete_one(user)
            flash("User profile deleted")
            return redirect(url_for("admin"))
        else:
            # redirect if not admin
            flash("Please login as admin")
            return redirect(url_for("index"))
    else:
        # redirect if no user logged in
        flash("Please login as admin")
        return redirect(url_for("index"))


# function for admin to change other user status
@app.route("/admin_status/<username>")
def admin_status(username):

    # check if user is logged in
    if "user" in session:

        # get user admin status from db
        admin = mongo.db.users.find_one(
            {"username": session["user"]})["admin"]

        if admin:

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
        else:
            # redirect if not admin
            flash("Please login as admin")
            return redirect(url_for("index"))
    else:
        # redirect if no user logged in
        flash("Please login as admin")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)

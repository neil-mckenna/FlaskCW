from flask import Flask, render_template, redirect, url_for, request, jsonify, make_response, flash, session
import os
import json
from datetime import datetime

# above import relevant librabies for funcitonality

# start a Flask class constructed with app name which is this app.py
app = Flask(__name__)

# this is needed for flashing messages
app.secret_key = "mehthisisecretkey44"


# a helper filter to show dates
@app.template_filter('dateformat')
def dateformat(value):
    return datetime.strptime(value, "%Y-%m-%d").strftime("%B %d, %Y")

# hard code const for the data file in my project for teh json data
DATA_FILE = os.path.join(os.path.dirname(__file__), 'static/jsonData','games.json')

# user data
USER_DATA_FILE = os.path.join(os.path.dirname(__file__), 'static/jsonData','users.json')

# load user data from JSOn file
def load_user_data():
    response, status_code = read_json_file(USER_DATA_FILE)

    if status_code == 200:
        # load users
        return response.get("data", {"users": []})

    # for error
    return {"users" : [] }


# save user data to JSON file
def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# a useful fucntion to extract josn data from a file as will reuse in multiple routes
def read_json_file(file_path):
    """
    this is a helper function to try an reads a json file,
    it tries to parse a python data structure, and will respond accordingly

    :param file_path: str - the path to teh JSON file
    :return: tuple - a dictionary containing the status ("status" or "error"),
    along with the parsed data, or an error message, alos with a status code
    - 200 success
    - 404 for file not found
    - 500 for server or other exceptions
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        return {
            "status" : "success",
            "data" : data
             }, 200
    except FileNotFoundError:
        return {
            "status" : "error",
            "message" : "File not found"
        }, 404
    except Exception as e:
        return {
            "status" : "error",
            "message" :  "Exception: " + str(e)
        }, 500


# start of routes
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # load exist users
        user_data = load_user_data()

        # if user already exists
        if any(user['username'] == username for user in user_data['users']):
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for('register'))

        # add new users
        user_data['users'].append({"username": username, "password": password})
        save_user_data(user_data)

        flash("Registration successful! Please log in: ", "success")
        return redirect(url_for('login'))

    return render_template('pages/security/register.html')

# login logic
@app.route('/login', methods=['GET','POST'])
def login():

    # hard code values for login
    H_USERNAME = "neil"
    H_PASSWORD = "password"

    # check for a post request
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # check against hardcoded values
        if username == H_USERNAME and password == H_PASSWORD:
            session['logged_in'] = True # set login status
            session['username'] = username

            # flash green
            flash("Login Successfully", "success")
            return redirect(url_for('home'))

        user_data = load_user_data()
        # this is  fancy lamda/forloop to compare usernames
        user = next((user for user in user_data['users'] if user['username'] == username), None)

        # if user password in key match the password
        if user and user['password'] == password:
            session['logged_in'] = True
            session['username'] = username
            flash("login successfully", "success")
            return redirect(url_for('home'))

        # failed both
        else:
            flash("Invalid details: username and or password. Please Try Again!", "danger")
            return redirect(url_for('login') )

    return render_template("pages/security/login.html")

# logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash("You have been logged out", "info")
    session.clear()
    return redirect(url_for('login'))

# deafult root or home index
@app.route('/')
def home():

    # redirect to login security reasons
    if not session.get('logged_in', False):
        return redirect(url_for('login'))

    # destruture function call with const from above
    response, status_code = read_json_file(DATA_FILE)

    # debug print
    print(response["data"])

    # if success
    if status_code == 200:
        # return page with data passed
        return render_template(
            'pages/index.html',
            games=response["data"],
            logged_in=session.get('logged_in', False))
    else:
        # return error message, status
        return jsonify(response), status_code


@app.route('/review/<int:id>/')
def individual_review(id=1):
    if id is None:
        id = 1  # default

    # destruture function call with const from above
    response, status_code = read_json_file(DATA_FILE)

    games = response["data"]

    review = next((game for game in games if game.get("id") == id), None)

    # protection from no data or bad id, the default parameter may get around
    # this but unless there isnt a corresponding review data
    if review is None:
        return f"Review with ID {id} not found.", 404

    total_reviews = len(games)  # Total number of reviews

    return render_template('pages/individual_review.html', review_id=id, review=review, total_reviews=total_reviews)


# about route
@app.route('/about')
def about():
    return render_template('pages/about.html')


# latest route
@app.route('/Top_10')
def latest():
    # read json
    response, status_code = read_json_file(DATA_FILE)

    # check if OK
    if status_code == 200:
        games = response["data"]

        # initialize an array
        all_reviews = []

        # loop through and check if review exists then add them to all_reviews
        print(games)

        for game in games:
            if game['review_full'] is not None:
                all_reviews.append(game)
            else:
                print("No Review in " + game)

        # put all review in a order of date of review
        all_reviews.sort(key=lambda x: datetime.strptime(x["review_date"], "%Y-%m-%d"), reverse=True)

        # garb the lastest 10
        latest_reviews = all_reviews[:10]

        # return a webpage with the data top reviews past
        return render_template('pages/latest.html', reviews=latest_reviews)
    else:
        return jsonify(response), status_code

# top 10
@app.route('/top_10')
def top_10():
    # read json
    response, status_code = read_json_file(DATA_FILE)

    # check if OK
    if status_code == 200:
        games = response["data"]

        # initialize an array
        all_reviews = []

        # loop through and check if review exists then add them to all_reviews
        print(games)

        for game in games:
            if game['review_full'] is not None:
                all_reviews.append(game)
            else:
                print("No Review in " + game)

        # put all review in a order of review score
        all_reviews.sort(reverse=True, key=lambda x: x['score'])

        # garb the lastest 10
        latest_reviews = all_reviews[:10]

        # return a webpage with the data top reviews past
        return render_template('pages/top_10.html', reviews=latest_reviews)
    else:
        return jsonify(response), status_code

#

@app.route('/all_reviews/')
@app.route('/all_reviews/<platform>/')
def all_reviews(platform=None):
    # Read the JSON file
    response, status_code = read_json_file(DATA_FILE)

    if status_code == 200:
        games = response.get("data", [])  # Use "games" from the response
    else:
        return jsonify(response), status_code

    # If a platform is provided in the URL, filter games by that platform
    if platform:

        print("Platform Passed: ", platform)
        games = [game for game in games if has_platform(game, platform.lower())]

    # Sort reviews based on the query parameter 'sort_by'
    sort_by = request.args.get('sort_by', 'score')
    print(f"Sort by: {sort_by}")

    # Check if the sort_by query parameter is related to a platform
    if sort_by.startswith('platform_'):
        platform = sort_by.replace('platform_', '').replace('_', ' ').title()  # Example: "xbox one" -> "Xbox One"
        # Filter the games that have the requested platform
        games = [game for game in games if has_platform(game, platform)]

    elif sort_by == 'score':
        games = sorted(games, key=lambda x: x['score'], reverse=True)

    elif sort_by == 'release_date':
        games = sorted(games, key=lambda x: int(f"{x['release_year']}{x['release_month']:02d}01"), reverse=True)

    elif sort_by == 'genre':
        games = sorted(games, key=lambda x: x['genre'])

    # Now you can sort by any other criteria if you want
    sorted_reviews = games

    # Extract unique platforms from all games
    platforms = sorted(set(platform for game in games for platform in game['platforms']), key=lambda p: p.lower())

    #print("Platforms: ",platforms)

    return render_template('pages/all_reviews.html', reviews=sorted_reviews, selected_platform=platform, platforms=platforms)



def has_platform(game, platform):
    """
    if check and comapre if in list then return a bool
    """
    return platform.lower() in [p.lower() for p in game['platforms']]

@app.route('/test/')
def test():
    game = {
        "id": 1,
        "name": "Super Mario Odyssey",
        "platforms": ["Nintendo Switch", "Wii U"]
    }

    platform_to_check = "Nintendo Switch"

    if has_platform(game, platform_to_check):
        return f"{platform_to_check} is available for {game['name']}"
    else:
        return f"{platform_to_check} is not available for {game['name']}"



# run app guard with debug
if __name__ == '__main__':
    app.run(debug=True)
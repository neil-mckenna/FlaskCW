from flask import Flask, render_template, redirect, url_for, request, jsonify, make_response
import os
import json

# above import relevant librabies for funcitonality

# start a Flask class constructed with app name which is this app.py
app = Flask(__name__)


# hard code const for the data file in my project for teh json data
DATA_FILE = os.path.join(os.path.dirname(__file__), 'static/jsonData','games.json')


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

# deafult root or home index
@app.route('/')
def home():
    # destruture function call with const from above
    response, status_code = read_json_file(DATA_FILE)

    # debug print
    print(response["data"])

    # if success
    if status_code == 200:
        # return page with data passed
        return render_template('pages/index.html', games=response["data"])
    else:
        # return error message, status
        return jsonify(response), status_code

# about route
@app.route('/about')
def about():
    return render_template('pages/about.html')


# top 10 route
@app.route('/Top_10')
def top_10():

    return render_template('top_10.html')



# run app guard with debug
if __name__ == '__main__':
    app.run(debug=True)
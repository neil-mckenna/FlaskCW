from flask import Flask, render_template, redirect, url_for, request, jsonify, make_response


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('base.html')

if __name__ == '__main__':
    app.run(debug=True)
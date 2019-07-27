from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session

import json
import os

import auth
import settings
from questions import Question

app = Flask(__name__)
app.register_blueprint(auth.gauth)
app.secret_key = settings.FLASK_SECRET



@app.route("/")
@auth.ensure_logged_in
def index():
    return render_template('index.html', questions=Question.active())

@app.route("/ask", methods=["POST"])
@auth.ensure_logged_in
def ask():
    result = request.form

    q = Question.new_question()
    q.question = result['question']
    q.asker = result['asker']
    q.save()

    return redirect(url_for('index'))

@app.route("/vote/<id>", methods=['GET'])
@auth.ensure_logged_in
def vote(id):
    q = Question.get(id)
    q.vote_for()

    return redirect(url_for('index'))
    

if __name__ == '__main__':
    app.run(debug = True)
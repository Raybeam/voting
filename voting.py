from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import json
import redis

app = Flask(__name__)

r = redis.StrictRedis(
    host='localhost', 
    port=6379, 
    db=0, 
    charset="utf-8", 
    decode_responses=True
    )
namespace = "voting"

@app.route("/")
def index():
    questions = get_active()
    return render_template('index.html', questions=questions)

@app.route("/ask", methods=["POST"])
def ask():
    result = request.form
    save_result(result)
    return redirect(url_for('index'))

@app.route("/vote/<id>", methods=['GET'])
def vote(id):
    r.incr("%s:votes" % id)
    return redirect(url_for('index'))  

def get_new_key():
    id = r.incr("%s_id_gen" % namespace)
    return "%s:%d" % (namespace, id)

def get_active():
    members = []
    for active in r.smembers('%s_active' % namespace):
        active = str(active)
        k = '%s:question' % active
        member = {
            'id': active,
            'question': r.get("%s:question" % active),
            'asker': r.get("%s:asker" % active),
            'votes': r.get("%s:votes" % active)
        }
        members.append(member)

    return members

def save_result(result):
    k = get_new_key()
    r.set("%s:question" % k, result['question'])
    r.set("%s:asker" % k, result['asker'])
    r.incr("%s:votes" % k)

    r.sadd("%s_all" % namespace, k)
    r.sadd("%s_active" % namespace, k)
    
    

if __name__ == '__main__':
    app.run(debug = True)
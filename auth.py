import settings

from flask import Blueprint
from flask import url_for
from flask import redirect
from flask import session
from flask_oauth import OAuth

from functools import wraps
from functools import update_wrapper

from urllib.request import urlopen, Request
from urllib.error import URLError
import json
import hashlib

gauth = Blueprint('gauth', __name__, template_folder='templates')

oauth = OAuth()
google = oauth.remote_app('google',
    base_url='https://www.google.com/accounts/',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    request_token_url=None,
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email',
        'response_type': 'code'
    },
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_method='POST',
    access_token_params={'grant_type': 'authorization_code'},
    consumer_key=settings.GOOGLE_CLIENT_ID,
    consumer_secret=settings.GOOGLE_CLIENT_SECRET
 )


@gauth.route('/login')
def login():
    callback=url_for('gauth.authorized', _external=True)
    return google.authorize(callback=callback)

@gauth.route(settings.REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')

def ensure_logged_in(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        set_session()

        access_token = session.get('access_token')
        if access_token is None:
            return redirect(url_for('gauth.login'))

        return f(*args, **kwargs)

    return update_wrapper(wrapper, f)

def set_session():
    access_token = session.get('access_token')
    if not access_token:
        return

    headers = {'Authorization': 'OAuth '+session['access_token'][0]}
    req = Request(
        'https://www.googleapis.com/oauth2/v1/userinfo',
        None,
        headers
    )

    try:
        res = urlopen(req)
        user_info = json.loads(res.read())

        h = hashlib.md5()
        salted = "%s.%s" % (user_info['id'], settings.FLASK_SECRET)
        h.update(salted.encode('utf-8'))
        session['user_id'] = h.hexdigest()
    except URLError as e:
        print(e)
        if e.code == 401:
            session.pop('access_token', None)


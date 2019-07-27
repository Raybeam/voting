import settings

from flask import Blueprint 
from flask_oauth import OAuth

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
    callback=url_for('authorized', _external=True)
    return auth.google.authorize(callback=callback)

@gauth.route(settings.REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')

def is_logged_in():
    return True if AUTH_TOKEN_KEY in flask.session else False
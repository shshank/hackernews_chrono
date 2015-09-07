
import datetime

from flask import Flask, request, g
from flask.ext import restful
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.session import Session

from configs import config
from utils import log_to_time_log


class FlaskConfig():
    DEBUG = config.DEBUG
    PORT = config.PORT
    SQLALCHEMY_DATABASE_URI = config.DATABASE_URI
    SECREY_KEY = 'tumtothehrepardesi'
    SESSION_TYPE = 'filesystem'

app = Flask(__name__)
app.config.from_object(FlaskConfig)

sess = Session()
sess.init_app(app)


db = SQLAlchemy(app, session_options={'expire_on_commit': False})


@app.before_request
def add_begin_time_to_g():
    g.begin_time = datetime.datetime.now()


@app.after_request
def after_request_calls(response):
    if config.DEBUG:
        now = datetime.datetime.now()
        diff = now - g.begin_time
        log_to_time_log(response_time=diff, request=request, response=response)
        return response


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()
    db.session.close()
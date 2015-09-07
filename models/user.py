import datetime
import time
from app_objects import db
from utils import app_exceptions
from werkzeug.security import generate_password_hash, check_password_hash

CHARS_ALLOWED_IN_USERNAME = [chr(item) for item in range(48, 58)+range(65, 91)+[95]+range(97, 123)]
USER_TYPES = {'admin': 5, 'normal': 0}


class User(db.Model):
    __tablename__   = 'users'
    __table_args__  = (db.Index('username_index', 'username'),)
    id              = db.Column(db.Integer(), primary_key=True)
    username        = db.Column(db.String(100), nullable=False, unique=True)
    password        = db.Column(db.String(200), nullable=False)
    user_type       = db.Column(db.Integer(), nullable=False)

    registered_at   = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.now())
    last_login_at   = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.now())
    registration_ip = db.Column(db.String(50))
    last_login_ip   = db.Column(db.String(50))

    email           = db.Column(db.String(200))
    bio             = db.Column(db.String(500))
    link            = db.Column(db.String(200))

    def __init__(self, username, password, registered_at=None, registration_ip=None,
                 user_type=0, email=None, bio=None, link=None, created_at=None):
        self.set_username(username)
        self.set_password(password)

        self.registered_at    = registered_at or datetime.datetime.now()
        self.last_login_at    = created_at or datetime.datetime.now()
        self.registration_ip  = registration_ip
        self.last_login_ip    = registration_ip
        self.user_type        = user_type
        self.email            = email
        self.bio              = bio
        self.link             = link

    @classmethod
    def add_new(cls, username, password, user_type=0):
        user = cls(username=username, password=password, user_type=user_type)
        db.session.add(user)
        db.session.commit()
        return user

    def __repr__(self):
        return "<User %r:%r>" % (self.id, self.username)

    def to_dict(self, viewer_id=None, get_full=None):
        user_dict = {
            'type':      'user',
            'id':        self.id,
            'username':  self.username,
            'email':     self.email,
            'user_type': self.user_type
            }
        if get_full or viewer_id == self.id:
            user_dict.update({
                'last_login_at': int(time.mktime(self.last_login_at.timetuple())),
                'last_login_ip': self.last_login_ip,
                'registered_at': int(time.mktime(self.registered_at.timetuple()))
                })
        return user_dict

    @staticmethod
    def is_valid_password(password):
        if password and len(password) >= 6:
            return True
        return False

    @staticmethod
    def is_valid_username(username):
        if username and len(username) >= 6:
            for char in username:
                if char not in CHARS_ALLOWED_IN_USERNAME:
                    return False
            return True
        return False

    def set_username(self, username):
        if not self.is_valid_username(username):
            raise app_exceptions.BadRequestException("username must be 6 characters or long and must only comprise or alpanumeric characters and underscore(_)")
        if bool(self.query.filter(User.username==username).first()):
            raise app_exceptions.BadRequestException("Username already taken")
        self.username = username

    def set_password(self, password):
        if not self.is_valid_password(password):
            raise app_exceptions.BadRequestException("Password must be a 6 characters or long")
        self.password = generate_password_hash(str(password))

    def check_password(self, password):
        return check_password_hash(str(self.password), str(password))

    @classmethod
    def get_user(cls, id):
        return cls.query.filter(cls.id==id).first()

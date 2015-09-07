import datetime
import time
from app_objects import db

class UserPostAction(db.Model):
    __tablename__  = 'user_post_actions'
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id'), db.Index('post_action_index', 'user_id', 'post_id'), )

    id             = db.Column(db.Integer(), primary_key=True)
    user_id        = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    post_id        = db.Column(db.Integer(), db.ForeignKey('posts.id'), nullable=False)
    marked_read    = db.Column(db.Boolean(), default=False)
    marked_deleted = db.Column(db.Boolean(), default=False)

    def __init__(self, user_id, post_id, marked_read=None, marked_deleted=None):

        if not any([marked_read == None, marked_deleted == None]):
            raise Exception("Can't insert blank row to UserPostAction. Either marked_read or marked_deleted must be provided.")

        self.user_id          = user_id
        self.post_id          = post_id
        self.marked_read      = marked_read or False
        self.marked_deleted   = marked_deleted or False

    @classmethod
    def add_action(cls, user_id, post_id, marked_read=None, marked_deleted=None):

        if not any([marked_read == None, marked_deleted == None]):
            raise Exception("Can't insert blank row to UserPostAction. Either marked_read or marked_deleted must be provided.")

        existing_item = cls.query.filter(cls.user_id == user_id,
                                         cls.post_id == post_id).first()

        if existing_item:
            existing_item.marked_read      = marked_read or False
            existing_item.marked_deleted   = marked_deleted or False
            action = existing_item

        else:
            action = cls(user_id=user_id, post_id=post_id, marked_read=marked_read, marked_deleted=marked_deleted)

        db.session.add(action)
        db.session.commit()
        return action


    def __repr__(self):
        return "<UserPostAction user_id=%r: post_id=%r: read=%r: deleted=%r>" % (self.user_id, self.post_id, self.marked_read, self.marked_deleted)

    def to_dict(self):
        resp_dict = {
            'type':             'user_post_action',
            'id':               self.id,
            'user_id':          self.user_id,
            'post_id':          self.post_id,
            'marked_read':      self.marked_read,
            'marked_deleted':   self.marked_deleted
        }
        return resp_dict

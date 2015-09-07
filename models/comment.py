import datetime
import time
from app_objects import db

class Comment(db.Model):
    __tablename__    = 'comments'
    __table_args__   = (db.Index('comment_index', 'post_id', 'deleted'),)
    id               = db.Column(db.Integer(), primary_key=True)
    post_id          = db.Column(db.Integer(), db.ForeignKey('posts.id'), nullable=False)
    parent           = db.Column(db.Integer(), db.ForeignKey('comments.id'), nullable=False)
    immediate_parent = db.Column(db.Integer(), db.ForeignKey('comments.id'), nullable=False)
    text             = db.Column(db.Text(), nullable=False)
    by               = db.Column(db.String(100), nullable=False)
    created_at       = db.Column(db.DateTime(), nullable=False)
    deleted          = db.Column(db.Boolean(), nullable=False, default=False)
    source           = db.Column(db.String(50), nullable=False)

    first_fetch_at   = db.Column(db.DateTime(), nullable=False)
    last_fetch_at    = db.Column(db.DateTime(), nullable=False)

    def __init__(self, id, post_id, parent, text, by, created_at=None,
                 first_fetch_at=None, last_fetch_at=None, deleted=False,
                 immediate_parent=None, source='HN'):

        self.id               = id
        self.post_id          = post_id
        self.parent           = parent
        self.text             = text
        self.by               = by
        self.created_at       = created_at
        self.first_fetch_at   = first_fetch_at or datetime.datetime.now()
        self.last_fetch_at    = last_fetch_at or datetime.datetime.now()
        self.deleted          = deleted
        self.immediate_parent = immediate_parent
        self.source           = source

    @classmethod
    def add_comment(cls, id, post_id, parent, text, by, created_at=None,
                 first_fetch_at=None, last_fetch_at=None, deleted=False,
                 immediate_parent=None, source='HN'):

        existing_item = self.query.filter(Comment.id == id).first()

        if existing_item:
            existing_item.text = text
            existing_item.deleted = deleted
            comment = existing_item
        
        else:
            comment = cls(id=id,
                          post_id=post_id,
                          parent=parent,
                          text=text,
                          by=by,
                          created_at=created_at,
                          first_fetch_at=first_fetch_at,
                          last_fetch_at=last_fetch_at,
                          deleted=deleted,
                          immediate_parent=immediate_parent,
                          source=source)
        db.session.add(comment)
        db.session.commit()



    def __repr__(self):
        return "<Comment post_id=%r: by=%r: parent=%r>" % (self.post_id, self.by, self.parent)

    def to_dict(self, viewer_id=None):
        resp_dict = {
            'type':             'comment',
            'post_id':          self.post_id,
            'parent':           self.parent,
            'immediate_parent': self.immediate_parent,
            'text':             self.text,
            'by':               self.by,
            'by_link':          "https://news.ycombinator.com/user?id={username}".format(username=self.by),
            'created_at':       int(time.mktime(self.created_at.timetuple())),
        }

    @classmethod
    def get_comments(cls, post_id):
        comments = cls.query.filter(cls.post_id == post_id).order_by(cls.created_at.desc()).all()
        return comments

    @staticmethod
    def nest_comments(comments):
        from collections import defaultdict
        top_level_comments = filter(lambda comment: not comment.parent, comments)

        for top_comment in top_level_comments:
            get_all_child_comments = lambda comment: comment.parent == top_comment.id

        nested_comments = defaultdict(list)
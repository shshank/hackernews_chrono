import datetime
import time
from app_objects import db
from sqlalchemy.sql import text
from user_action import UserPostAction
import utils

class Post(db.Model):
    __tablename__     = 'posts'
    __table_args__    = (db.Index('post_index', 'created_at', 'post_type', 'deleted'),)
    id                = db.Column(db.Integer(), primary_key=True)
    deleted           = db.Column(db.Boolean(), nullable=False)
    post_type         = db.Column(db.String(100), nullable=False)
    by                = db.Column(db.String(100), nullable=False)
    created_at        = db.Column(db.DateTime(), nullable=False)
    score             = db.Column(db.Integer(), nullable=False, default=0)
    comment_count     = db.Column(db.Integer(), nullable=False, default=0)
    source            = db.Column(db.String(50), nullable=False)
    rank_when_fetched = db.Column(db.Integer(), nullable=False)
    url               = db.Column(db.String(500))
    title             = db.Column(db.String(500))
    text              = db.Column(db.Text())
    dead              = db.Column(db.Boolean())
    parent            = db.Column(db.Integer())
    first_fetch_at    = db.Column(db.DateTime())
    last_fetch_at     = db.Column(db.DateTime())

    def __init__(self, id, post_type, by, created_at, url, rank_when_fetched,
                 score=0, comment_count=0, title=None, text=None, dead=False,
                 parent=None, first_fetch_at=None, last_fetch_at=None, deleted=False,
                 source='HN'):

        self.id                = id
        self.deleted           = bool(deleted)
        self.post_type         = post_type
        self.by                = by
        self.created_at        = created_at
        self.url               = url
        self.score             = score
        self.comment_count     = comment_count
        self.title             = title
        self.text              = text
        self.dead              = dead
        self.parent            = parent
        self.first_fetch_at    = first_fetch_at or datetime.datetime.now()
        self.last_fetch_at     = last_fetch_at or datetime.datetime.now()
        self.source            = source
        self.rank_when_fetched = rank_when_fetched

    def __repr__(self):
        return "<Post %r:%r:%r>" % (self.id, self.post_type, self.title)

    @classmethod
    def add_post(cls, id, post_type, by, created_at, url, rank_when_fetched,
                 score=0, comment_count=0, title=None, text=None, dead=False,
                 parent=None, first_fetch_at=None, last_fetch_at=None, deleted=False,
                 source='HN'):

        existing_item = cls.query.filter(Post.id == id).first()

        if existing_item:
            existing_item.comment_count     = comment_count
            existing_item.score             = score
            existing_item.deleted           = bool(deleted)
            existing_item.title             = title
            existing_item.text              = text
            existing_item.rank_when_fetched = rank_when_fetched
            existing_item.last_fetch_at     = last_fetch_at
            post = existing_item

        else:
            post = cls(id=id,
                       post_type=post_type,
                       by=by,
                       created_at=created_at,
                       url=url,
                       rank_when_fetched=rank_when_fetched,
                       score=score,
                       comment_count=comment_count,
                       title=title,
                       text=text,
                       dead=dead,
                       parent=parent,
                       first_fetch_at=first_fetch_at,
                       last_fetch_at=last_fetch_at,
                       deleted=deleted,
                       source=source,
                       )
        db.session.add(post)
        db.session.commit()
        return post

    @classmethod
    def to_dict(cls, post, viewer_id=None, include_action_data=True):
        post_dict = {
            'type':           'post',
            'post_type':      post.post_type,
            'id':             post.id,
            'deleted':        post.deleted,
            'by':             post.by,
            'by_link':        "https://news.ycombinator.com/user?id={username}".format(username=post.by),
            'created_at':     int(time.mktime(post.created_at.timetuple())),
            'url':            post.url,
            'score':          post.score,
            'comment_count':  post.comment_count,
            'title':          post.title,
            'text':           post.text,
            'dead':           post.dead,
            'parent':         post.parent,
            'viewer_read':    None,
            'viewer_deleted': None,
            'hn_link':        "https://news.ycombinator.com/item?id={id}".format(id=post.id),
            'time_string':    utils.human_friendly_datetime(post.created_at),
            'domain':         utils.get_domain_from_url(post.url)
            }
        if viewer_id and include_action_data:
            user_post_action = UserPostAction.query.filter(UserPostAction.user_id == viewer_id,
                                                           UserPostAction.post_id == post.id).first()
            if user_post_action:
                post_dict['viewer_read']    = user_post_action.marked_read
                post_dict['viewer_deleted'] = user_post_action.marked_deleted
        return post_dict

    @classmethod
    def get_posts(cls, viewer_id=None, offset=0, limit=20):
        last_fetched_post = cls.query.with_entities(cls.last_fetch_at).filter(
                                                   ).order_by(cls.last_fetch_at.desc()
                                                   ).first()
        if not last_fetched_post:
            return []
        else:
            last_fetch_at = last_fetched_post.last_fetch_at
            query = text("""SELECT posts.* FROM posts
                            LEFT JOIN user_post_actions on user_post_actions.post_id=posts.id
                            WHERE posts.deleted=False
                                AND posts.post_type='story'
                                AND posts.last_fetch_at=:last_fetch_at
                                AND (user_post_actions.user_id is NULL or user_post_actions.user_id=:viewer_id)
                                AND (user_post_actions.marked_deleted is NULL or user_post_actions.marked_deleted=false)
                                AND (user_post_actions.marked_read is NULL or user_post_actions.marked_read=false)
                            ORDER BY posts.created_at DESC
                            LIMIT :offset, :limit
                         """
                        )
        posts = list(db.session.execute(query, params={'viewer_id': viewer_id, 'offset': offset,
                                                       'limit': limit, 'last_fetch_at': last_fetch_at
                                                      }
                                        )
                    )
        return posts

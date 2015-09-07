import datetime

from hackernews import fetch_posts
from models import Post, db
from utils.error_handler import report_error
from utils import app_exceptions

def run_scraper():
    try:
        fetch_time = datetime.datetime.now()
        post_dicts = fetch_posts(from_page_num=1, to_page_num=3)
        post_dicts.sort(key=lambda p: p['id'])
        
        for post_dict in post_dicts:
            print post_dict['id'], post_dict['title'].encode('utf-8')
            Post.add_post(id=post_dict['id'],
                          post_type=post_dict['post_type'],
                          by=post_dict['by'],
                          created_at=post_dict['created_at'],
                          url=post_dict['url'],
                          rank_when_fetched=post_dict['rank'],
                          score=post_dict['score'],
                          comment_count=post_dict['comment_count'],
                          title=post_dict['title'],
                          last_fetch_at=fetch_time
                          )
    except Exception as e:
        report_error(e, raise_again=False)
        raise app_exceptions.ScraperError("Something went wrong with the scraper, error has been reported.")
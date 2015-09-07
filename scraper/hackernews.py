import requests
import time
import datetime
from bs4 import BeautifulSoup as bsoup

listing_url = "https://news.ycombinator.com/news?p={page_num}"
single_post_url = "https://news.ycombinator.com/item?id={post_id}"


def get_page_content(url):
    """
    Fetches a page and return content.
    Raises exception if non 200 response.

    Returns string (HTML is case of HN pages.)
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
    resp = requests.get(url=url, headers=headers)
    if resp.status_code == 200:
        return resp.content
    raise Exception("Non 200 response from url: %s" % url)


def get_time_from_created_at_text(created_at_text):
    """
    Converts HN time format to datetime
    e.g. "1 hour ago" become datetime object of now() - 1 hour.
    
    returns datetime object
    """
    text = created_at_text.rstrip(' ago')

    numeric_value = int(text.split()[0])

    if 'hour' in text:
        timediff = datetime.timedelta(hours=numeric_value)
    elif 'minute' in text:
        timediff = datetime.timedelta(minutes=numeric_value)
    elif 'second' in text:
        timediff = datetime.timedelta(seconds=numeric_value)
    elif 'day' in text:
        timediff = datetime.timedelta(days=numeric_value)
    elif 'month' in text:
        timediff = datetime.timedelta(months=numeric_value)

    return datetime.datetime.now() - timediff


def get_posts_from_listing(page_num):
    """
    For a given page number, fetched all posts from that hackernews page.

    Returns a list of dictionary, each dictionary represents a post.
    """
    html = get_page_content(url=listing_url.format(page_num=page_num))
    soup = bsoup(html)

    post_details = []

    post_title_item = soup.find('tr', {"class": "athing"})
    while post_title_item:
        
        #TO GET: rank, title, url

        rank = post_title_item.find_next('span', {'class': 'rank'}).text.strip('.') 
        rank = int(rank)

        title_text_item = post_title_item.find_next('td', {'class': 'title'}
                                                    ).findNext('td', {'class': 'title'}
                                                    ).find('a')
        title = title_text_item.text.strip()
        url = title_text_item.get('href')

        
        #Parsing the lower subtext part.
        post_details_item = post_title_item.findNext('tr')


        #TO GET: score, post_type
        post_type = 'job'
        score = 0
        score_item = post_details_item.find_next('span', {'class': 'score'})
        if score_item:
            post_type = 'story'
            score = int(score_item.text.split()[0])

        
        #TO GET: created_at, comment_count, by, post_id

        #initialising just in case the data is not found below.
        #Assuming that the numbers are not as important as the news item appearing in users feed is.
        created_at = datetime.datetime.now()
        comment_count = 0
        by = ''
        
        all_a = post_details_item.find_all('a')
        for a in all_a:
            if 'user' in a.get('href'):
                by = a.text
            elif 'comment' in a.text:
                comment_count = int(a.text.split()[0])
            elif 'ago' in a.text:
                created_at = get_time_from_created_at_text(created_at_text=a.text)
                post_id = int(a.get('href').lstrip('item?id='))

        if post_type=='story':
            post_dict = {
                'id':  post_id,
                'rank': rank,
                'title': title,
                'url': url,
                'score': score,
                'created_at': created_at,
                'comment_count': comment_count,
                'by': by,
                'post_type': post_type
                }
            post_details.append(post_dict)

            post_title_item = post_title_item.findNext('tr', {"class": "athing"})

    return post_details


def fetch_posts(from_page_num, to_page_num):
    """
    Fetches post details from HN starting from from_page_num to to_page_num

    Returns a list of dictionary, each dictionary represents a post.
    """
    from_page_num = max(from_page_num, 1)

    #must be =<from_page_num and less than 15(last page at HN)
    to_page_num = min(15, max(from_page_num, to_page_num)) 

    post_details = []
    for page_num in range(from_page_num, to_page_num+1):
        post_details_for_page = get_posts_from_listing(page_num=page_num)
        post_details.extend(post_details_for_page)
        print page_num
    print len(post_details)
    return post_details




if __name__ == '__main__':
    fetch_posts(14, 30)

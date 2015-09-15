from error_handler import report_error
import datetime
import time
from configs import config
from urllib2 import urlparse


def log_to_time_log(response_time, request, response):
    try:
        now = datetime.datetime.now()
        now_string = now.strftime("%Y-%m-%d %H:%M:%S.%f")

        log_string = ' :: '.join([
            str(response_time),
            response.status,
            request.headers.get('X-Forward-For', request.headers.get('X-Real-IP') or request.remote_addr),
            request.url,
            request.headers.get('User-Agent', 'NA'),
            now_string
            ]) + '\n'

        with open(config.REQUEST_TIME_LOG_FILE_NAME, 'a') as f:
            f.write(log_string)
    except Exception as e:
        report_error(e, raise_again=False)


def human_friendly_datetime(date_time):
    """
    converts a python datetime object to the
    format "X days ago"

    #TODO: Test it well, written in a hurry. Also find a better way. Assuming 30 day months and 365 days year
    """
    current_datetime = datetime.datetime.now()
    delta = current_datetime - date_time
    total_seconds = int(delta.total_seconds())

    if total_seconds < 60:
        time_string = "Few seconds ago"

    elif total_seconds >= 60 and total_seconds < 60*60:
        minutes = total_seconds/60
        minute_string = "minutes" if minutes > 1 else "minute"
        time_string = "{0} {1} ago".format(minutes, minute_string)

    elif total_seconds >= 60*60 and total_seconds < 60*60*24:
        hours = total_seconds/(60*60)
        hour_string = "hours" if hours > 1 else "hour"
        time_string = "{0} {1} ago".format(hours, hour_string)

    elif delta.days >= 1:
        days = delta.days
        day_string = "days" if days > 1 else "day"
        time_string = "{0} {1} ago".format(days, day_string)

    elif delta.days >= 30 and delta.days < 365:
        months = delta.days/30
        month_string = "months" if months > 1 else "month"
        time_string = "{0} {1} ago".format(months, month_string)

    elif delta.days >= 365:
        years = delta.days/365
        year_string = "years" if years > 1 else "year"
        time_string = "{0} {1} ago".format(years, year_string)

    #just in case I have missed a case. Need to test.
    else:
        time_string = str(date_time)

    return time_string


def get_domain_from_url(url):
    """
    return 'xyx.com' for 'http://www.xyz.com/abc.html'
    return the input in case of error while parsing.
    """
    try:
        netloc = urlparse.urlparse(url).netloc
        domain = '.'.join(netloc.split('.')[1:]) if netloc.startswith('www.') else netloc
        return domain
    except:
        return url


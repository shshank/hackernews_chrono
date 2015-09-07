import traceback


def report_error(e, email_ids=None, custom_data=None, raise_again=True):
    """
    Use this function to mail or log errors to a bug tracking system. Leaving skeletal.
    """
    print traceback.format_exc(e)
    if raise_again:
        raise e

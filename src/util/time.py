import datetime


def get_now():
    return datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
import datetime


def get_now():
    return datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
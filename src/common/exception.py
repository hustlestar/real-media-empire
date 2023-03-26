class WrongMediaException(Exception):
    def __init__(self, msg):
        super(WrongMediaException, self).__init__(msg)

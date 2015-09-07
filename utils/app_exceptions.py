class BadRequestException(Exception):

    def __init__(self, value='Invalid Request'):
        self.value = value

    def __str__(self):
        return self.value
class SolveFrameException(Exception):
    pass


class BadNumberError(SolveFrameException):
    def __init__(self, number):
        super().__init__("unable to correct number: {}".format(number))

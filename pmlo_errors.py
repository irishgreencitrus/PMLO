import sys
from contextlib import contextmanager


class PMLOBaseException(Exception):
    pass


class PMLOLabelNotFoundError(PMLOBaseException):
    def __init__(self, label):
        self.label = label
        super().__init__(f"Label {self.label} not found in file, unable to jump.")


class PMLOFunctionNotFoundError(PMLOBaseException):
    def __init__(self, function):
        self.function = function
        super().__init__(f"Function {self.function} not found")


def pmlo_handler(type, value, traceback):
    print(f"\n\nAn error occured while interpreting PMLO\n{str(type.__name__)}: {str(value)}")


@contextmanager
def pmlo_handle_except(exc_handler):
    sys.excepthook = exc_handler
    yield
    sys.excepthook = sys.__excepthook__

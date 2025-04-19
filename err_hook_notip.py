import sys
from log import *

def except_hook(exc_type, exc_value, exc_traceback): ...

sys.excepthook = except_hook
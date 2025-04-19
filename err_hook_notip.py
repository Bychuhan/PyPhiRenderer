import sys
import traceback
from log import *

def except_hook(exc_type, exc_value, exc_traceback):
    pass

sys.excepthook = except_hook
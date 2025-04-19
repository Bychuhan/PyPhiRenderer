import sys
import traceback
from log import *

def except_hook(exc_type, exc_value, exc_traceback):
    track = traceback.format_exception(exc_value)
    error(f"\n{'\n'.join(track)}")

sys.excepthook = except_hook
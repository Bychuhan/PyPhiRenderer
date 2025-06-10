import time
import traceback
import sys
import os

def header():
    filename, line_number, function_name, text = traceback.extract_stack()[-3]
    return f"\033[38;2;218;112;214m[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]\033[0m \033[38;2;255;192;203m[{os.path.splitext(os.path.basename(filename))[0]}::{function_name}::{line_number}]\033[0m"

def debug(text, end="\n"):
    print(f"{header()}\033[38;2;135;206;250m [DEBUG]\033[0m {text}",end=end)

def info(text, end="\n"):
    print(f"{header()}\033[0m\033[38;2;127;255;170m [INFO]\033[0m {text}",end=end)

def warning(text, end="\n"):
    print(f"{header()}\033[0m\033[38;2;255;255;106m [WARNING]\033[0m {text}",end=end)

def error(text, end="\n"):
    print(f"{header()}\033[0m\033[38;2;255;99;71m [ERROR]\033[0m {text}",end=end)

def critical(text, end="\n"):
    print(f"{header()}\033[0m\033[38;2;255;0;0m [CRITICAL]\033[0m {text}",end=end)

def error_and_exit_no_tip(text):
    error(text)
    sys.exit(1)
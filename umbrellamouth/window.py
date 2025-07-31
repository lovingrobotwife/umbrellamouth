
import subprocess
from umbrellamouth import *

def get_window_title():
    return subprocess.run(
        ['xdotool', 'getactivewindow', 'getwindowname'],
        text=True,
        capture_output=True
    ).stdout.strip()

@with_cursor
def resolve_window(cursor=None):
    for entry, attrs in parse(get_window_title(), cursor=cursor):
        return entry, attrs 
    return None, None

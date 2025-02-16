# ref: https://stackoverflow.com/a/14981125
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

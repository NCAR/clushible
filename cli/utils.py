#/opt/clmgr/python-310/bin/python3.10

import sys

def warn(msg:str):
    sys.stderr.write(f"WARN: {msg}")
    sys.stderr.flush()

def error(msg:str, rc=1):
    sys.stderr.write(f"ERROR: {msg}. ({rc})")
    sys.exit(rc)

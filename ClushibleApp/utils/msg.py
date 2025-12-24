import sys


def info(msg: str):
    sys.stdout.write(f"INFO: {msg}\n")


def warn(msg: str):
    sys.stderr.write(f"WARN: {msg}\n")
    sys.stderr.flush()


def error(msg: str, rc=1):
    sys.stderr.write(f"ERROR: {msg} ({rc})\n")
    sys.exit(rc)

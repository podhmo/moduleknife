import sys


def modulename_of(path):
    """module name from filepath"""
    if not path.endswith((".py", ".pyc")):
        return path
    for syspath in sys.path:
        path = path.replace(syspath, "")
    if path.endswith(".pyc"):
        path = path[:-1]
    path = path.replace("/__init__.py", "").rsplit(".py", 1)[0]
    return path.lstrip("/").replace("/", ".")


def is_modulename(name):
    if "/" in name:
        return False
    return True

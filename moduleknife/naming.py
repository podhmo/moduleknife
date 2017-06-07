import sys

sys_paths = None


def modulename_of(path, reload=False):
    """module name from filepath"""
    global sys_paths
    if reload or sys_paths is None:
        sys_paths = sorted(sys.path, key=lambda x: -len(x))

    if not path.endswith((".py", ".pyc")):
        return path
    for syspath in sys_paths:
        path = path.replace(syspath, "")
    if path.endswith(".pyc"):
        path = path[:-1]
    path = path.replace("/__init__.py", "").rsplit(".py", 1)[0]
    return path.lstrip("/").replace("/", ".")


def is_modulename(name):
    if "/" in name:
        return False
    return True

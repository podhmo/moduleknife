from moduleknife.capture import capture
from moduleknife.naming import modulename_of, is_modulename


def display(src, dst):
    if is_modulename(modulename_of(dst)):
        print("@", modulename_of(src), modulename_of(dst))


with capture(display):
    import wsgiref.simple_server  # NOQA

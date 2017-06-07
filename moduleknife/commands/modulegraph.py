from moduleknife.capture import capture_with_signal_handle
from moduleknife.calling import call_file_as_main_module, call_command_as_main_module
from moduleknife.graph import Digraph
from moduleknife.naming import modulename_of, is_modulename
from magicalimport import import_symbol
import sys
import os.path
import shutil

dag = Digraph()


def add(src, dst):
    if is_modulename(modulename_of(dst)):
        dag.add(modulename_of(src), modulename_of(dst))


def on_stop(signum, tb):
    filename = "/tmp/graph.dot"
    with open(filename, "w") as wf:
        wf.write(str(dag.to_dot()))
    print("write {}...".format(filename), file=sys.stderr)


def run(file):
    sys.argv.pop(1)

    if ":" in file:
        return import_symbol(file)()
    elif os.path.exists(file):
        return call_file_as_main_module(file)

    cmd_path = shutil.which(file)
    if cmd_path:
        return call_command_as_main_module(file, cmd_path)


def main():
    if len(sys.argv) <= 1:
        print("modulegraph <filename>")
        sys.exit(1)

    with capture_with_signal_handle(add, teardown=on_stop):
        run(sys.argv[1])

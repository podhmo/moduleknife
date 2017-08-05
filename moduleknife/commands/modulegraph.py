from moduleknife.capture import capture_with_signal_handle
from moduleknife.calling import call_file_as_main_module, call_command_as_main_module
from moduleknife.graph import Digraph, DigraphToplevelOnly
from moduleknife.naming import modulename_of, is_modulename
from magicalimport import import_symbol
import argparse
import sys
import os.path
import shutil


class Driver:
    factory = Digraph

    def __init__(self, filename):
        self.dag = self.factory()
        self.filename = filename

    def add(self, src, dst):
        if is_modulename(modulename_of(dst)):
            self.dag.add(modulename_of(src), modulename_of(dst))

    def finish(self, signum, tb):
        if self.filename is None:
            sys.stdout.write(str(self.dag.to_dot()))
        else:
            with open(self.filename, "w") as wf:
                wf.write(str(self.dag.to_dot()))
            print("write {}...".format(self.filename), file=sys.stderr)

    def run(self, fname, extras):
        sys.argv = [sys.argv[0]]
        sys.argv.extend(extras)

        if ":" in fname:
            return import_symbol(fname)()
        elif os.path.exists(fname) and not os.path.isdir(fname):
            return call_file_as_main_module(fname)

        cmd_path = shutil.which(fname)
        if cmd_path:
            return call_command_as_main_module(fname, cmd_path)


class ToplevelOnlyDriver(Driver):
    factory = DigraphToplevelOnly


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("file")
    parser.add_argument("--outfile", default=None)
    parser.add_argument(
        "--driver",
        default="moduleknife.commands.modulegraph:Driver",
        help="default: moduleknife.commands.modulegraph:Driver",
    )

    args, extras = parser.parse_known_args()

    driver_cls = import_symbol(args.driver, ns="moduleknife.commands.modulegraph")
    driver = driver_cls(args.outfile)

    with capture_with_signal_handle(driver.add, teardown=driver.finish):
        driver.run(args.file, extras)

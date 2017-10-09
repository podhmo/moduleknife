from moduleknife.capture import capture_with_signal_handle
from moduleknife.calling import call_file_as_main_module, call_command_as_main_module
from moduleknife.graph import Digraph, DigraphToplevelOnly
from moduleknife.naming import modulename_of, is_modulename
from magicalimport import import_symbol
import argparse
import sys
import time
import os.path
import shutil


class Driver:
    factory = Digraph

    def __init__(self, filename, metadata_handler):
        self.dag = self.factory()
        self.filename = filename
        self.metadata_handler = metadata_handler

    def add(self, src, dst, *, stage):
        metadata = self.metadata_handler.handle(src, dst, stage=stage)
        if stage == "after" and is_modulename(modulename_of(dst)):
            self.dag.add(modulename_of(src), modulename_of(dst), metadata=metadata)

    def finish(self, signum, tb):
        if self.filename is None:
            sys.stdout.write(str(self.dag.to_dot(self.metadata_handler.emit)))
            self.metadata_handler.finish(sys.stdout)
        else:
            with open(self.filename, "w") as wf:
                wf.write(str(self.dag.to_dot(self.metadata_handler.emit)))
                self.metadata_handler.finish(wf)
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


def convert_size(size_bytes):
    import math
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


class timeHandler:
    def __init__(self):
        self.before_map = {}
        self.results = {}

    def handle(self, src, dst, *, stage):
        if stage == "before":
            self.before_map[dst] = time.time()
            return None
        else:
            r = self.results[dst] = time.time() - self.before_map[dst]
            return r

    def emit(self, m, graph, src, dst):
        m.stmt('{} -> {} [label="{}s"]', graph[src], graph[dst], round(graph.metadata[dst], 5))

    def finish(self, wf):
        top_n_items = sorted([(v, k) for k, v in self.results.items()], reverse=True)
        print("", file=wf)
        for t, name in top_n_items:
            print("// load {} ... {}s".format(name, t), file=wf)


class memoryHandler:
    def __init__(self):
        import psutil
        self.p = psutil.Process()
        self.before_map = {}
        self.results = {}

    def handle(self, src, dst, *, stage):
        if stage == "before":
            self.before_map[dst] = self.p.memory_info().rss
            return None
        else:
            r = self.results[dst] = self.p.memory_info().rss - self.before_map[dst]
            return r

    def emit(self, m, graph, src, dst):
        m.stmt('{} -> {} [label="{}"]', graph[src], graph[dst], convert_size(graph.metadata[dst]))

    def finish(self, wf):
        top_n_items = sorted([(v, k) for k, v in self.results.items()], reverse=True)
        print("", file=wf)
        for v, name in top_n_items:
            print("// load {} ... {}".format(name, convert_size(v)), file=wf)


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("file")
    parser.add_argument("--outfile", default=None)
    parser.add_argument("--metadata", choices=["time", "memory"], default="time")
    parser.add_argument(
        "--driver",
        default="moduleknife.commands.modulegraph:Driver",
        help="default: moduleknife.commands.modulegraph:Driver",
    )
    args, extras = parser.parse_known_args()

    driver_cls = import_symbol(args.driver, ns="moduleknife.commands.modulegraph")
    metadata_handler = globals().get(args.metadata + "Handler", timeHandler)()
    driver = driver_cls(args.outfile, metadata_handler)

    with capture_with_signal_handle(driver.add, teardown=driver.finish):
        driver.run(args.file, extras)

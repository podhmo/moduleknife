import contextlib
from collections import defaultdict
from prestring import Module


class DotModule(Module):
    @contextlib.contextmanager
    def block(self, value=""):
        self.stmt("{}{{".format(value))
        with self.scope():
            yield
        self.stmt("}")


class GensymMap:
    def __init__(self, prefix="g"):
        self.prefix = prefix
        self.d = {}
        self.i = 0

    def __contains__(self, name):
        return name in self.d

    def __getitem__(self, name):
        if name in self.d:
            return self.d[name]
        self.d[name] = v = "{}{}".format(self.prefix, self.i)
        self.i += 1
        return v


class Digraph:
    def __init__(self):
        self.nodes = defaultdict(set)
        self.gensym_map = GensymMap("g")
        self.metadata = {}

    def __getitem__(self, k):
        return self.gensym_map[k]

    def add(self, src, dst, metadata=None):
        if src == dst:
            return
        self.nodes[src].add(dst)
        if self.metadata is not None:
            self.metadata[dst] = metadata

    def to_dot(self, handle=None):
        m = DotModule()
        with m.block("digraph g "):
            for src, dsts in self.nodes.items():
                if src not in self.gensym_map:
                    m.stmt('{} [label="{}"]'.format(self.gensym_map[src], src))
                for dst in dsts:
                    if dst not in self.gensym_map:
                        m.stmt('{} [label="{}"]'.format(self.gensym_map[dst], dst))
            for src, dsts in self.nodes.items():
                for dst in dsts:
                    if handle:
                        handle(m, self, src, dst)
                    else:
                        m.stmt("{} -> {}", self.gensym_map[src], self.gensym_map[dst])
        return str(m)


class DigraphToplevelOnly(Digraph):
    def add(self, src, dst):
        return self._add(src.split(".", 1)[0], dst.split(".", 1)[0])

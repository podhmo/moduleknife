import contextlib


@contextlib.contextmanager
def subparser(subparsers, fn, *args, name=None, **kwargs):
    name = name or fn.__name__
    parser = subparsers.add_parser(name, *args, **kwargs)
    dests = []
    arrived = set()

    def add_argument(*args, **kwargs):
        ac = parser.add_argument(*args, **kwargs)
        if ac.dest not in arrived:
            arrived.add(ac.dest)
            dests.append(ac.dest)
        return ac

    yield add_argument

    def run(args, *, extras):
        return fn(extras=extras, **{name: getattr(args, name) for name in dests})

    parser.set_defaults(fn=run)

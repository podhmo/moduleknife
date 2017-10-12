import sys
import argparse
from magicalimport import import_symbol
from moduleknife.commands import subparser
from moduleknife import calling


def capture(*, command, outfile, interval, display_function, extras, **kwargs):
    from moduleknife.ticker import tick, setup
    from moduleknife.display import RemoteDisplay

    fn = import_symbol(display_function)

    # factory object
    if isinstance(fn, type):
        if outfile is None:
            output = sys.stderr
        else:
            output = open(outfile, "w")
            import atexit

            def message():
                output.close()
                print("write {} ...".format(outfile), file=sys.stderr)

            atexit.register(message)

        fn = RemoteDisplay(fn(output))

    setup()
    cancel = tick(fn, interval=interval)  # noqa
    return calling.call_file(command, extras)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.required = True

    with subparser(subparsers, capture, add_help=False) as add_argument:
        add_argument("--outfile", default=None)
        add_argument("--interval", default=0.5, type=float)
        add_argument("--display-function", default="moduleknife.display:DefaultDisplay")
        add_argument("command")

    args, extras = parser.parse_known_args()
    return args.fn(args, extras=extras)

import sys
from moduleknife.capture import capture_with_signal_handle
from moduleknife.graph import Digraph
from moduleknife.naming import modulename_of, is_modulename

dag = Digraph()


def add(src, dst, *, stage):
    if stage == "before":
        if is_modulename(modulename_of(dst)):
            dag.add(modulename_of(src), modulename_of(dst))


def on_stop(signum, tb):
    print(dag.to_dot())
    sys.stdout.flush()


with capture_with_signal_handle(add, teardown=on_stop):
    from wsgiref.simple_server import make_server
    from pyramid.config import Configurator
    from pyramid.response import Response

    def hello_world(request):
        return Response('Hello %(name)s!' % request.matchdict)

    def main():
        config = Configurator()
        config.add_route('hello', '/hello/{name}')
        config.add_view(hello_world, route_name='hello')
        app = config.make_wsgi_app()
        server = make_server('0.0.0.0', 8080, app)
        server.serve_forever()

    main()

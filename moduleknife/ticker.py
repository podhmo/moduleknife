import logging
import threading

logger = logging.getLogger(__name__)


class Ticker:
    def __init__(self, fn, *, interval, iterations=-1, failfast=False):
        self.fn = fn
        self.interval = interval
        self.iterations = iterations
        self._started = False
        self.failfast = failfast

    def start(self):
        if self._started:
            raise RuntimeError("already started")

        def ticker():
            if self.iterations != 0:
                self.iterations -= 1
                t = threading.Timer(self.interval, ticker, [])
                t.setDaemon(True)
                t.start()
            try:
                self.fn()
            except:
                logger.info("error in ticker", exc_info=True)
                if self.failfast:
                    raise

        ticker()

    def cancel(self):
        self.iterations = 0


def tick(fn, *, interval, iterations=-1, failfast=False):
    t = Ticker(fn, interval=interval, iterations=iterations, failfast=failfast)
    t.start()
    return t.cancel


def setup(level=logging.DEBUG):
    import sys

    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)

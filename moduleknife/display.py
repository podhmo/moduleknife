import sys
import os
import signal


class ProcessInfoDisplay:
    def __init__(self, output):
        import psutil

        self.output = output
        self.p = psutil.Process()

    def collect_process_info(self):
        p = self.p
        d = {}
        with p.oneshot():
            d["pid"] = p.pid
            d["memory_info"] = p.memory_info()._asdict()
            d["cpu_times"] = p.cpu_times()._asdict()
            d["cpu_percent"] = p.cpu_percent()
            d["memory_percent"] = p.memory_percent()
        return d

    def __call__(self):
        print(self.collect_process_info(), file=self.output)


class TracebackDisplay:
    def __init__(self, output, level=3):
        import traceback

        self.output = output
        self.skip_level = level
        self.traceback = traceback

    def collect_stack(self, limit=5):
        f = sys._getframe(self.skip_level)
        return self.traceback.format_list(self.traceback.extract_stack(f, limit=limit))

    def __call__(self):
        print("----------------------------------------", file=self.output)
        for item in self.collect_stack():
            print(item, file=self.output, end="")


class RemoteDisplay:
    def __init__(self, display):
        self.ping = _get_display_function_in_current_thread(display)

    def __call__(self):
        self.ping()


class DefaultDisplay:
    def __init__(self, output, level=4):
        import json

        self.output = output
        self.process = ProcessInfoDisplay(output)
        self.stacktrace = TracebackDisplay(output, level=level)
        self.json = json

    def __call__(self):
        info = self.process.collect_process_info()
        stack = self.stacktrace.collect_stack()
        d = {"stack": stack}
        d.update(info)
        self.json.dump(d, self.output, indent=2, ensure_ascii=False, sort_keys=True)


def _get_display_function_in_current_thread(display, sig=signal.SIGUSR1):
    def handle_ping(sig, frame):
        display()

    pid = os.getpid()
    signal.signal(sig, handle_ping)

    def ping():
        return os.kill(pid, signal.SIGUSR1)

    return ping

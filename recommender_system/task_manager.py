import multiprocessing
import threading
import time

from recommender_system.workflow import main
from web_app.util import MessageQueue


class Sequencer:
    def __init__(self, interval=60 * 1):
        self._lock = threading.Lock()
        self._interval = interval
        self._g = self.__generator()

    def __generator(self):
        while True:
            time.sleep(self._interval)
            yield True

    def wait(self):
        with self._lock:
            next(self._g)
            return True


def monitor_signal(timer):
    with MessageQueue() as mq:
        while True:
            mq.wait_refresh_signal()  # block wait
            timer.wait()
            p = multiprocessing.Process(target=main)
            p.start()
            p.join()


def task_timer(timer):
    while True:
        timer.wait()
        p = multiprocessing.Process(target=main)
        p.start()
        p.join()


def run():
    timer = Sequencer(interval=60 * 1)
    threading.Thread(target=monitor_signal, args=(timer,)).start()
    threading.Thread(target=task_timer, args=(timer,)).start()


if __name__ == '__main__':
    run()

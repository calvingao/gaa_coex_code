# Derived from multiprocessing.pool for Non-Daemonic use
# Nested Pools are possible
import multiprocessing.pool


class NoDaemonProcess(multiprocessing.Process):

    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False

    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)


class Pool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess

from __future__ import absolute_import, division

def init():
    import signal

    from pyranha.engine.engine import Engine

    engine = Engine()
    engine.start()

    def sigint(signum, frame):
        print 'stopping'
        engine.running = False

    signal.signal(signal.SIGINT, sigint)

    engine.join()

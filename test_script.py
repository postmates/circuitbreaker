from circuitbreaker import CircuitBreaker

import os
import multiprocessing
import time

prefix = "unforked"

def p(message):
    print(prefix + ": " + message)

p("program starting")
v = multiprocessing.Value('i')
p("about to fork")
v.value = 0
l = multiprocessing.Lock()
A= CircuitBreaker(failure_threshold=8, name="rogan-tset", expected_exception=ValueError, recovery_timeout=8)

@A
def test():
    raise ValueError("sorry rogan")

class B(object):
    def __init__(self):
        self.val = multiprocessing.Value('i', 0)

    def inc(self):
        with self.val.get_lock():
            self.val.value += 1


if os.fork():
    prefix = "parent"
    # b = B()
    for i in xrange(10):
        with A._state.get_lock():
            p("parent state of cb before:" + A.state + " failure count:" + str(A.failure_count))
        try:
            test()
        except Exception as e :
            print("parent " + str(e))
            with A._state.get_lock():
                p("parent state of cb after:" + A.state + " failure count:" + str(A.failure_count))
            time.sleep(3)


    os.wait()
    p("parent says value is: %s" % (A.state,))
else:
    prefix = "child"
    for i in xrange(10):
        with A._state.get_lock():
            p("child state of cb before:" + A.state + " failure count:" + str(A.failure_count))
        try:
            test()
        except Exception as e:
            print("child " + str(e))
            with A._state.get_lock():
                p("child state of cb after:" + A.state + " failure count:" + str(A.failure_count))
            time.sleep(3)


p(prefix + " program ending")

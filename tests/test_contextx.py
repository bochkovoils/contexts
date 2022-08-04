import time

from contexts import __version__
from pytest import fixture
from pytest_bdd import given, then, when, scenarios, parsers
from abc import abstractmethod
from datetime import datetime, timedelta

scenarios("features")

class GlobalContainer:
    VALUE = None
    COUNT = 0


@fixture(autouse=True)
def f_1():
    GlobalContainer.VALUE = datetime.now() + timedelta(seconds=30)

@fixture(autouse=True)
def f_2():
    GlobalContainer.COUNT = 0

class ContextBlock:
    def __init__(self):
        self.steps = []

    def append(self, obj):
        self.steps.append(obj)

    @abstractmethod
    def execute(self):
        pass

    def run_all(self):
        for step in self.steps:
            step()


class AwaitBlock(ContextBlock):
    def __init__(self, seconds, wait_seconds=1):
        super().__init__()
        self.seconds = seconds
        self.wait_seconds = wait_seconds

    def execute(self):
        stop_time = datetime.now() + timedelta(seconds=self.seconds)
        err = None
        while datetime.now() < stop_time:
            try:
                self.run_all()
                return
            except AssertionError as e:
                time.sleep(self.wait_seconds)
                err = e
        raise err


class MustFailBlock(ContextBlock):
    def execute(self):
        try:
            self.run_all()
            assert False
        except Exception:
            assert True

class RepeatBlock(ContextBlock):
    def __init__(self, times=10):
        super().__init__()
        self.times = times

    def execute(self):
        for i in range(self.times):
            self.run_all()

class ContextHolder:
    CONTEXTS = []

    def is_active(self):
        return len(ContextHolder.CONTEXTS) == 0

    def get_current(self):
        return self.CONTEXTS[-1]

    def add(self, context_block):
        ContextHolder.CONTEXTS.append(context_block)

    def pop(self):
        return ContextHolder.CONTEXTS.pop()

    def __len__(self):
        return len(ContextHolder.CONTEXTS)


def context_step():
    def result(method):
        def ret(*objs, **kwargs):
            if not ContextHolder().is_active():
                ContextHolder().get_current().append(lambda: method(*objs, **kwargs))
                return
            return method(*objs, **kwargs)
        return ret
    return result


@given("hello")
@context_step()
def hello():
    assert True


@given("assert global time")
@context_step()
def assert_something():
    if GlobalContainer.VALUE > datetime.now():
        assert False
    assert True


@given(parsers.parse("AWAIT {seconds_} await {await_}"))
def set_await_context(seconds_, await_):
    ContextHolder().add(AwaitBlock(int(seconds_), int(await_)))


@given(parsers.parse("REPEAT {count}"))
def repeat_context(count):
    ContextHolder().add(RepeatBlock(int(count)))


@given(parsers.parse("MUST FAIL"))
def must_fail_block():
    ContextHolder().add(MustFailBlock())


@given(parsers.parse("TRY"))
def set_await_context(seconds_, await_):
    ContextHolder().add(AwaitBlock(int(seconds_), int(await_)))


@given("Value must be more then 10")
@context_step()
def check_value():
    assert GlobalContainer.COUNT > 10


@given("Add 1")
@context_step()
def add_1():
    GlobalContainer.COUNT += 1


@given("END")
def end_context():
    if len(ContextHolder()) > 0:
        current = ContextHolder().pop()
        if len(ContextHolder()) > 0:
            ContextHolder().get_current().append(lambda: current.execute())
        else:
            current.execute()
    else:
        raise Exception("END не обособляет контекст")


def test_version():
    assert __version__ == '0.1.0'

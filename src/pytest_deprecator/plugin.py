import pytest


class Deprecator:
    def pytest_sessionstart(self, session):
        print("START")

    def pytest_sessionfinish(self, session, exitstatus):
        print("FINISH")

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write("Oh Hello!")

    @pytest.hookimpl()
    def pytest_runtestloop(self, *args, **kwargs):
        print("RUN TESTLOOP")

    @pytest.hookimpl()
    def pytest_runtest_protocol(self, *args, **kwargs):
        print("RUN PROTOCOL")

    @pytest.hookimpl()
    def pytest_runtest_logstart(self, *args, **kwargs):
        print("RUN LOGSTART")

    @pytest.hookimpl()
    def pytest_runtest_logfinish(self, *args, **kwargs):
        print("RUN LOGFINISH")

    @pytest.hookimpl()
    def pytest_runtest_setup(self, *args, **kwargs):
        print("RUN SETUP")

    @pytest.hookimpl()
    def pytest_runtest_call(self, *args, **kwargs):
        print("RUN CALL")

    @pytest.hookimpl()
    def pytest_runtest_teardown(self, *args, **kwargs):
        print("RUN TEARDOWN")

    @pytest.hookimpl()
    def pytest_runtest_makereport(self, *args, **kwargs):
        print("RUN MAKEREPORT")


def pytest_addoption(parser):
    group = parser.getgroup('deprecator-pytest')
    group.addoption(
        '--use-deprecate',
        action='store_true',
        help='Whether to use depreactor or not'
    )

    # parser.addini('HELLO', 'Dummy pytest.ini setting')


def pytest_configure(config):
    config.pluginmanager.register(Deprecator())


@pytest.fixture
def fake_warning():
    print("OK")
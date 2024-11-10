from dataclasses import dataclass, field
import warnings
from typing import Literal

import pytest


@dataclass
class DeprecatorReport:
    warnings: dict = field(default_factory=dict)
    total_count: int = 0



class Deprecator:
    def __init__(self, *args, **kwargs):
        self.report = DeprecatorReport()

    def pytest_sessionstart(self, session):
        print("START")

    def pytest_sessionfinish(self, session, exitstatus):
        print("FINISHED")
        print("Report Deprecations")
        for warning_name, warning_data in self.report.warnings.items():
            print(f"{warning_name}: Had {warning_data['count']} occurances")
        print("End Report")

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

    @pytest.hookimpl()
    def pytest_warning_recorded(self,
        warning_message: warnings.WarningMessage,
        when: Literal["config", "collect", "runtest"],
        nodeid: str,
        location: tuple[str, int, str] | None):
        if warning_message.category == DeprecationWarning:
            warning_name = warning_message.message.args[0]

            if not self.report.warnings.get(warning_name):
                self.report.warnings[warning_name] = {
                    'count': 1
                }
            else:
                self.report.warnings[warning_name]['count'] += 1


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

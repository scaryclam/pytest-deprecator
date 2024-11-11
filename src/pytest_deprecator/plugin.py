import os
from dataclasses import dataclass, field
import warnings
from typing import Literal

import pytest


@dataclass
class DeprecatorReport:
    warnings: dict = field(default_factory=dict)
    total_count: int = 0


class Deprecator:
    report = None

    def pytest_sessionstart(self, session):
        #import ipdb
        #ipdb.set_trace()
        self.report = DeprecatorReport()
        self.session_failed = False
        self.allowed_warnings = 7

    def pytest_sessionfinish(self, session, exitstatus):
        for warning_name, warning_data in self.report.warnings.items():
            count = warning_data['count']

            if count > self.allowed_warnings:
               session.exitstatus = 101
               session.config.stash[pytest.StashKey["bool"]()] = True
               self.session_failed = True

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.ensure_newline()
        title = 'deprecations report summary'
        terminal_kwargs = {'bold': True}
        if self.session_failed:
            title += ' (failed)'
            terminal_kwargs['red'] = True
        else:
            title += ' (passed)'
            terminal_kwargs['green'] = True
        terminalreporter.section(title, sep='=', **terminal_kwargs)

        content = []
        for warning_name, warning_data in self.report.warnings.items():
            content.append(f"{warning_name}: Had {warning_data['count']} occurances")

        terminalreporter.line(os.linesep.join(content))

    @pytest.hookimpl()
    def pytest_warning_recorded(self,
        warning_message: warnings.WarningMessage,
        when: Literal["config", "collect", "runtest"],
        nodeid: str,
        location: tuple[str, int, str] | None):
        if warning_message.category == DeprecationWarning:
            warning_name = warning_message.message.args[0]

            if self.report is None:
                return

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


def pytest_configure(config):
    config.pluginmanager.register(Deprecator())

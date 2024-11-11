import re
import os
from dataclasses import dataclass, field
import warnings
from typing import Literal

import pytest


@dataclass
class DeprecatorReport:
    warnings: dict = field(default_factory=dict)
    total_count: int = 0


@dataclass
class DeprecatorConfig:
    warning_configs: dict = field(default_factory=dict)


class Deprecator:
    report = None
    config = None

    def __init__(self, config):
        self.config = config

    def pytest_sessionstart(self, session):
        self.report = DeprecatorReport()
        self.session_failed = False
        self.allowed_warnings = self.config.warning_configs

    def pytest_sessionfinish(self, session, exitstatus):
        for warning_name, warning_data in self.report.warnings.items():
            allowed_warnings = 0
            skip_warning = True

            count = warning_data['count']
            #import ipdb
            #ipdb.set_trace()

            for warning_regex, allowed_number in self.config.warning_configs.items():
                result = re.search(warning_regex, warning_name)
                if result:
                    skip_warning = False
                    allowed_warnings = allowed_number
                    break

            if not skip_warning and count > allowed_warnings:
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
        help='Whether to use deprecator or not'
    )


def pytest_configure(config):
    ini_config = config.inicfg.get('deprecator_warnings', [])
    warning_dict = {}
    for warning_config in ini_config:
        allowed = int(warning_config.split(':')[-1])
        name = warning_config.split(':')[0]
        warning_dict[name] = allowed

    deprecator_config = DeprecatorConfig(warning_configs=warning_dict)
    config.pluginmanager.register(Deprecator(deprecator_config))

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

    def _find_warning(self, warning_name):
        for warning_regex, warning_data in self.config.warning_configs.items():
            result = re.search(warning_regex, warning_name, flags=re.MULTILINE|re.DOTALL)
            if result:
                return self.config.warning_configs[warning_regex]
        return None

    def pytest_sessionstart(self, session):
        self.report = DeprecatorReport()
        self.session_failed = False
        self.allowed_warnings = self.config.warning_configs

    def pytest_sessionfinish(self, session, exitstatus):
        for warning_name, warning_data in self.report.warnings.items():
            allowed_warnings = 0

            count = warning_data['count']

            warning_config = self._find_warning(warning_name)
            allowed_warnings = warning_config['allowed_number']
            action = warning_config['action']

            # Don't fail the session on a warning we just want to see in the reporting
            if action == 'error':
                if allowed_warnings is None:
                    allowed_warnings = 0

                if count > allowed_warnings:
                    session.exitstatus = 101
                    session.config.stash[pytest.StashKey["bool"]()] = True
                    self.session_failed = True
                    self.report.warnings[warning_name]['config'] = warning_config
                    self.report.warnings[warning_name]['result'] = 'fail'
                else:
                    self.report.warnings[warning_name]['config'] = warning_config
                    self.report.warnings[warning_name]['result'] = 'success'
            elif action == 'watch':
                self.report.warnings[warning_name]['result'] = 'report'

    def pytest_terminal_summary(self, terminalreporter):
        BOLD = '\033[1m'
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        END = '\033[0m'

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
        if self.report.warnings == {}:
            terminalreporter.line("No warnings to report on. Use deprecator_warnings in pyproject.toml for configure some", green=True)

        for warning_name, warning_data in self.report.warnings.items():
            # content.append(f"{warning_name}: Had {warning_data['count']} occurances")
            message = f"{warning_name}: {BOLD}Had {warning_data['count']} occurances{END}"
            if warning_data.get('result') == 'fail':
                message += f"{RED}{BOLD}, was allowed {warning_data['config']['allowed_number']}{END}"
                terminalreporter.line(message, red=True)
            if warning_data.get('result') == 'report':
                terminalreporter.line(message, blue=True)
            if warning_data.get('result') == 'success':
                message += f"{GREEN}{BOLD}, is allowed {warning_data['config']['allowed_number']}{END}"
                terminalreporter.line(message, green=True)

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

            warning_dict = self._find_warning(warning_name)
            if not warning_dict:
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
    if not config.getoption('use_deprecate'):
        return

    ini_config = config.inicfg.get('deprecator_warnings', [])
    warning_dict = {}
    for warning_config in ini_config:
        action = warning_config.split(':')[0]
        name = warning_config.split(':')[1]
        allowed_str = warning_config.split(':')[-1]
        if allowed_str:
            allowed = int(allowed_str)
        else:
            allowed = None
        warning_dict[name] = {'allowed_number': allowed, "action": action}

    deprecator_config = DeprecatorConfig(warning_configs=warning_dict)
    config.pluginmanager.register(Deprecator(deprecator_config))

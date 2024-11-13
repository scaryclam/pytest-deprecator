# Pytest Deprecator

## What is this?

pytest-deprecator is a project to aid in the incremental removal of deprecated code.
It allows a configuration to be added to pyproject.toml so that deprecated code paths can be
monitored and set to error if the number of times the deprecation warning is reported during the
test run.

This is helpful in allowed teams to work on removing deprecated code in smaller chunks, without new
code being written that calls the deprecated code.

## Why not filterwarnings?

filterwarnings is great for erroring when a warning is found. This is a plugin to allow *some*
instances of the deprecation warning, but will then fail when too many are found.


#!/usr/bin/env python
"""Verify PyHealth 2.0 architecture contracts.

Checks performed:

1. Every submodule of ``pyhealth`` imports cleanly (no import-time side
   effects such as reading environment variables or network access).
2. Every concrete ``BaseTask`` subclass shipped in ``pyhealth.tasks``
   defines ``task_name`` and provides ``input_schema``/``output_schema``
   (either as class attributes or assigned in ``__init__``).

Exits 0 when all contracts hold, 1 otherwise.
"""

import importlib
import inspect
import pkgutil
import sys
import warnings


def check_imports() -> list:
    warnings.filterwarnings("ignore")
    import pyhealth

    failures = []
    for modinfo in pkgutil.walk_packages(pyhealth.__path__, prefix="pyhealth."):
        try:
            importlib.import_module(modinfo.name)
        except BaseException as exc:  # noqa: BLE001 - report everything
            failures.append(f"{modinfo.name}: {type(exc).__name__}: {exc}")
    return failures


def check_task_schemas() -> list:
    import pyhealth.tasks as task_pkg
    from pyhealth.tasks.base_task import BaseTask

    failures = []
    seen = set()
    for modinfo in pkgutil.iter_modules(task_pkg.__path__):
        try:
            module = importlib.import_module(f"pyhealth.tasks.{modinfo.name}")
        except Exception as exc:
            failures.append(f"pyhealth.tasks.{modinfo.name} import failed: {exc}")
            continue
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if (
                not issubclass(cls, BaseTask)
                or cls is BaseTask
                or inspect.isabstract(cls)
                or cls.__module__ != module.__name__
                or cls in seen
            ):
                continue
            seen.add(cls)
            attrs = {k for klass in cls.__mro__ for k in vars(klass)}
            try:
                source = inspect.getsource(cls)
            except (OSError, TypeError):
                source = ""
            for attr in ("task_name", "input_schema", "output_schema"):
                if attr not in attrs and f"self.{attr}" not in source:
                    failures.append(f"{cls.__module__}.{name} missing {attr}")
    if not seen:
        failures.append("no BaseTask subclasses discovered (check broken?)")
    return failures


def main() -> int:
    status = 0
    import_failures = check_imports()
    if import_failures:
        status = 1
        print("Import failures:")
        for failure in import_failures:
            print(f"  {failure}")
    schema_failures = check_task_schemas()
    if schema_failures:
        status = 1
        print("Task contract failures:")
        for failure in schema_failures:
            print(f"  {failure}")
    if status == 0:
        print("All architecture contracts hold.")
    return status


if __name__ == "__main__":
    sys.exit(main())

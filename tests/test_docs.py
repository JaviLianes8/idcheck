"""Execute public docstrings and the README's Python examples."""

from __future__ import annotations

import ast
import doctest
import inspect
import re
from pathlib import Path

import idcheck


def test_every_public_name_has_a_runnable_example() -> None:
    for name in idcheck.__all__:
        assert ">>>" in (inspect.getdoc(getattr(idcheck, name)) or ""), name


def test_public_docstrings_execute_with_only_public_imports() -> None:
    finder = doctest.DocTestFinder()
    runner = doctest.DocTestRunner()
    namespace = {name: getattr(idcheck, name) for name in idcheck.__all__}
    for name, value in namespace.items():
        for example in finder.find(value, name=name, globs=namespace):
            runner.run(example)
    assert runner.summarize().failed == 0


def test_readme_python_examples_and_expected_expressions() -> None:
    text = (Path(__file__).parents[1] / "README.md").read_text(encoding="utf-8")
    namespace: dict[str, object] = {}
    for block in re.findall(r"```python\n(.*?)```", text, re.DOTALL):
        checked = []
        for line in block.splitlines():
            checked.append(line)
            if "  # " not in line or line.lstrip().startswith("#"):
                continue
            expression, expected = line.split("  # ", 1)
            if expected.startswith(("True", "False", "None", "Reason.", "1777", "1645", "'01FW")):
                expected = expected.split(" (")[0]
                ast.parse(expression.strip(), mode="eval")
                indentation = expression[: len(expression) - len(expression.lstrip())]
                checked[-1] = f"{indentation}assert ({expression.strip()}) == ({expected})"
        exec(compile("\n".join(checked), "README.md", "exec"), namespace)

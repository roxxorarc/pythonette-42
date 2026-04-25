from __future__ import annotations

import difflib
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pythonette.detector import Found

if TYPE_CHECKING:
    from pythonette.runner import ExerciseReport


class Printer:
    def __init__(
        self, verbose: bool = False, diff: bool = False, explain: bool = False
    ) -> None:
        self.verbose = verbose
        self.diff = diff
        self.explain = explain
        self.console = Console()

    def no_match(self, path: Path) -> None:
        self.console.print(
            Panel(
                Text.from_markup(
                    f"No 42 Python exercise detected in [bold]{path}[/].\n"
                    "Pythonette identifies exercises by their filenames."
                ),
                title="pythonette",
                border_style="yellow",
            )
        )

    def preamble(self, findings: list[Found]) -> None:
        table = Table(title="Detected exercises", header_style="bold cyan")
        table.add_column("Module")
        table.add_column("Exercise")
        table.add_column("File", overflow="fold")
        for f in findings:
            table.add_row(
                f.exercise.module_id, f.exercise.id, str(f.file)
            )
        self.console.print(table)

    def exercise_report(self, report: "ExerciseReport") -> None:
        ex = report.found.exercise
        title = f"module {ex.module_id} · {ex.id}"

        rows: list = []
        rows.append(self._style_row(report))
        for outcome in report.cases:
            rows.append(self._case_row(outcome))

        body = Group(*rows)

        if not report.ok and self.explain and ex.explain:
            body = Group(
                body,
                Panel(
                    Text(ex.explain, style="italic"),
                    title="hint",
                    border_style="cyan",
                ),
            )

        border = "green" if report.ok else "red"
        self.console.print(Panel(body, title=title, border_style=border))

    def _style_row(self, report: "ExerciseReport") -> Text:
        if not report.style:
            return Text("◯ style — no file checked", style="dim")
        bad = [s for s in report.style if not s.ok]
        if not bad:
            return Text("✓ flake8 — clean", style="green")
        out = Text()
        out.append("✗ flake8 — KO\n", style="bold red")
        for s in bad:
            out.append(s.output + "\n", style="red")
        return out

    def _case_row(self, outcome) -> Group:
        head = (
            Text("✓ ", style="green") + Text(outcome.case.name)
            if outcome.ok
            else Text("✗ ", style="bold red") + Text(outcome.case.name)
        )
        if outcome.ok:
            return Group(head)

        details: list = [head, Text(f"  {outcome.reason}", style="red")]
        if self.diff and outcome.case.expected_stdout is not None:
            details.append(
                self._diff_panel(
                    outcome.case.expected_stdout, outcome.result.stdout
                )
            )
        return Group(*details)

    def _diff_panel(self, expected: str, got: str) -> Panel:
        diff_lines = list(
            difflib.unified_diff(
                expected.splitlines(),
                got.splitlines(),
                fromfile="expected",
                tofile="got",
                lineterm="",
            )
        )
        text = Text()
        for line in diff_lines:
            style = ""
            if line.startswith("+") and not line.startswith("+++"):
                style = "green"
            elif line.startswith("-") and not line.startswith("---"):
                style = "red"
            elif line.startswith("@@"):
                style = "cyan"
            text.append(line + "\n", style=style)
        return Panel(text, title="diff", border_style="dim")

    def summary(self, total: int, failures: int) -> None:
        passed = total - failures
        style = "green" if failures == 0 else "red"
        self.console.print(
            Panel(
                Text.from_markup(
                    f"[bold]{passed}/{total}[/] exercises OK · "
                    f"[bold]{failures}[/] KO"
                ),
                border_style=style,
                title="summary",
            )
        )

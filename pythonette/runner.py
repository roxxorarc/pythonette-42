import argparse
from dataclasses import dataclass

from pythonette.checks import CheckResult
from pythonette.checkers.style import StyleResult, check_flake8, check_mypy
from pythonette.detector import Found, detect
from pythonette.printer import Printer


@dataclass
class ExerciseReport:
    found: Found
    style: list[StyleResult]
    results: list[CheckResult]

    @property
    def ok(self) -> bool:
        return (
            all(s.ok for s in self.style)
            and all(r.ok for r in self.results)
        )


def run(args: argparse.Namespace) -> int:
    printer = Printer(verbose=args.verbose, diff=args.diff, explain=args.explain)
    findings = detect(args.path)

    if args.module:
        findings = [f for f in findings if f.exercise.module_id == args.module]
    if args.exercise:
        findings = [f for f in findings if f.exercise.id == args.exercise]

    if not findings:
        printer.no_match(args.path)
        return 1

    printer.preamble(findings)

    by_exercise: dict[tuple[str, str], list[Found]] = {}
    for f in findings:
        by_exercise.setdefault((f.exercise.module_id, f.exercise.id), []).append(f)

    failures = 0
    for _, group in sorted(by_exercise.items()):
        report = _evaluate(group)
        printer.exercise_report(report)
        if not report.ok:
            failures += 1

    printer.summary(len(by_exercise), failures)
    return 0 if failures == 0 else 1


def _evaluate(group: list[Found]) -> ExerciseReport:
    exercise = group[0].exercise
    exercise_dir = group[0].file.parent

    style: list[StyleResult] = []
    py_files: list[Path] = []
    for fname in exercise.filenames:
        path = exercise_dir / fname
        if path.is_file():
            py_files.append(path)
    for extra in getattr(exercise, "support_paths", ()):
        extra_path = exercise_dir / extra
        if extra_path.is_file() and extra_path.suffix == ".py":
            py_files.append(extra_path)
        elif extra_path.is_dir():
            py_files.extend(
                p for p in extra_path.rglob("*.py")
                if "__pycache__" not in p.parts
            )
    mypy_skip = set(getattr(exercise, "mypy_skip", ()))
    for path in py_files:
        style.append(check_flake8(path))
        if path.name not in mypy_skip:
            style.append(check_mypy(path))

    results: list[CheckResult] = [
        check.run(exercise_dir, exercise) for check in exercise.checks
    ]

    return ExerciseReport(found=group[0], style=style, results=results)

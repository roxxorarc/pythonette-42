# WARNING: Please note that this project is in early development and may not be fully functional, if you notice any issues with the tests (e.g. false positives, false negatives or any other problems), please report them by opening an issue on GitHub with a detailed description. Thank you for your understanding and support !

# 🐍 pythonette

A test automation framework for the 42 Python modules.

`pythonette` runs flake8, executes each exercise against a battery of test cases, and reports the result with rich panels. It is designed to install and run on 42 workstations without any admin privileges.

## 📦 Install

### One-liner (recommended)

```sh
bash -c "$(curl -fsSL https://raw.githubusercontent.com/roxxorarc/pythonette-42/main/install.sh)"
```

### Manual

```sh
git clone https://github.com/roxxorarc/pythonette-42.git
cd pythonette-42
./install.sh
```

### After install

If `~/.local/bin` is not already on your `PATH`, the installer adds it
to `~/.zshrc` automatically. Apply it to your current session with:

```sh
source ~/.zshrc
```

Requirements: Python 3.10 or newer and `git`. No admin privileges required.

## 🚀 Usage

From inside any directory containing your exercise files:

```sh
pythonette                  # auto-detect, run every detected exercise
pythonette -m 00            # only module 00
pythonette -e ex02          # only the ex02 exercise (any module)
pythonette --diff           # show colored diffs on failure
pythonette --explain        # print a hint on each failure
pythonette -u               # git pull + reinstall
pythonette -V               # version
```

Detection is filename-based. A file like `ft_plot_area.py` is
identified as module 00 / ex02 regardless of where it sits in your
tree, so any layout works:

```
my_42_python/
├── python_module_00/ex2/ft_plot_area.py
└── python_module_01/ex0/ft_garden_intro.py
```

## 📚 Supported modules



## ✅ Checks

For each detected exercise:

1. **Style** — `flake8` and `mypy` (strict) run on every file in the
   exercise. Failures are listed inline but do not stop the rest of the
   checks. The mypy cache lives under `~/.cache/pythonette/mypy/` so
   warm runs are an order of magnitude faster than cold ones.
2. **Static checks** — AST-only assertions (`StructureCheck`,
   `AuthorizedCheck`, `ImportCheck`, …) verify structure without
   executing the student code.
3. **Runtime checks** — the student files are copied into a temp dir,
   then a generated harness imports/calls/runs them in a subprocess.
   Used for `SignatureCheck`, `AssertCheck`, `RunCheck`, `ScriptCheck`,
   etc. Default timeout: 5 seconds (treated as a possible infinite
   loop).
4. **Output matching** — stdout is matched against `expected_stdout`
   (exact) or `expected_contains` / `stdout_contains` (substring list).
   Non-zero exit codes and tracebacks surface as the failure reason.

The framework exposes a typed `Assertion` DSL (`Eq`, `IsInstance`,
`Raises`, `Prints`, `HasStaticMethod`, `FileWritten`, …) so test
authors declare *what* to verify rather than hand-writing harness code.


## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the architecture, the full
check toolbox, and a worked example of adding an exercise or a new
module.

## 📄 License

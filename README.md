# 🐍 pythonette

A test automation framework for the 42 Python modules.

`pythonette` runs flake8, executes each exercise against a battery of test cases, and reports the result with rich panels. It is designed to install and run on 42 workstations without any admin privileges.

## 📦 Install

```sh
git clone https://github.com/roxxorarc/pythonette-42.git
cd pythonette-42
./install.sh
```

If `~/.local/bin` is not on your `PATH`, the installer prints a one-line
snippet to add to your shell rc.

Requirements: Python 3.10 or newer. That is the only thing the host
machine has to provide.

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

1. **Norme** — `flake8` on every file. Failures are listed
   inline but do not stop the rest of the checks.
2. **Execution** — every `TestCase` for that exercise is run in an
   isolated temp directory (the student file is copied, nothing is
   written next to your code).
3. **Output** — stdout is matched against `expected_stdout` (exact)
   or `expected_contains` (substring list). Non-zero exit codes and
   timeouts (default 5s, treated as possible infinite loops) are
   reported.


## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add test cases,
exercises, and new modules.

## 📄 License

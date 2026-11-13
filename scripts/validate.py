"""Run the reviewed server tests in a disposable environment, locally and in CI."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
TEST_FILES = (
    'tests/test_sqlite_local.py',
    'tests/test_sqlite_concurrency.py',
    'tests/test_production_setup.py',
    'tests/test_validation_command.py',
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verbose', action='store_true', help='Show individual test names.')
    args = parser.parse_args(argv)

    # Configure the child BEFORE pytest imports application modules. Fixtures still
    # create their own files; this also isolates import-time create_app() calls.
    with tempfile.TemporaryDirectory(prefix='formiguinhas-validation-') as directory:
        temporary = Path(directory)
        environment = os.environ.copy()
        environment.update({
            'DATABASE_URL': f"sqlite:///{(temporary / 'main.db').as_posix()}",
            'PRE_CADASTRO_DATABASE_URL': f"sqlite:///{(temporary / 'pre.db').as_posix()}",
            'SESSION_FILE_DIR': str(temporary / 'sessions'),
            'APP_ENV': 'development',
            'FLASK_ENV': 'development',
            'FLASK_DEBUG': '0',
            'SECRET_KEY': 'validation-only-secret-never-use-in-production',
            'SQLITE_BUSY_TIMEOUT_MS': '10000',
            'OPENAI_API_KEY': '',
            'SENDGRID_API_KEY': '',
            'SENHA_ADMIN': '',
            # Avoid local plugins/addopts silently selecting external or old tests.
            'PYTEST_ADDOPTS': '',
            'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1',
        })
        environment.pop('PYTEST_PLUGINS', None)
        # Bypass pytest's shared pytest-of-<user> folder: it may have stale ACLs
        # on Windows. Only this new, uniquely owned subdirectory may be cleaned.
        command = [sys.executable, '-m', 'pytest', *TEST_FILES,
                   '--basetemp', str(temporary / 'pytest'),
                   '-v' if args.verbose else '-q', '--tb=short', '-o', 'addopts=']
        print('Validating isolated server tests (Playwright is not included).', flush=True)
        result = subprocess.run(command, cwd=ROOT, env=environment, check=False)
        if result.returncode == 0:
            print('Server validation passed. Browser validation is separate.', flush=True)
        else:
            print('Server validation failed. Review the pytest output above.', flush=True)
        return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())

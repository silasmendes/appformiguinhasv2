"""Protect the validation entry point against local data use and false success."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def validation():
    path = Path(__file__).resolve().parents[1] / 'scripts' / 'validate.py'
    spec = importlib.util.spec_from_file_location('validation_entry_point', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('exit_code', [0, 1, 5])
def test_validation_isolates_child_and_preserves_failure(validation, monkeypatch, tmp_path, exit_code):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///must-not-be-used.db')
    monkeypatch.setenv('PRE_CADASTRO_DATABASE_URL', 'sqlite:///must-not-be-used-pre.db')
    monkeypatch.setenv('OPENAI_API_KEY', 'fake-key-not-for-use')
    monkeypatch.setenv('SENDGRID_API_KEY', 'fake-key-not-for-use')
    monkeypatch.setenv('PYTEST_ADDOPTS', 'tests/test_playwright_atendimento.py')
    monkeypatch.setenv('PYTEST_PLUGINS', 'unreviewed_plugin')
    calls = []

    def run(command, *, cwd, env, check):
        directory = Path(env['SESSION_FILE_DIR']).parent
        assert directory.is_dir()
        assert not directory.is_relative_to(validation.ROOT)
        assert env['DATABASE_URL'] == f"sqlite:///{(directory / 'main.db').as_posix()}"
        assert env['PRE_CADASTRO_DATABASE_URL'] == f"sqlite:///{(directory / 'pre.db').as_posix()}"
        assert env['OPENAI_API_KEY'] == env['SENDGRID_API_KEY'] == ''
        assert env['APP_ENV'] == 'development'
        assert env['PYTEST_ADDOPTS'] == ''
        assert env['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] == '1'
        assert 'PYTEST_PLUGINS' not in env
        assert cwd == validation.ROOT
        assert check is False
        selected = {value for value in command if value.startswith('tests/')}
        assert selected == {
            'tests/test_sqlite_local.py', 'tests/test_sqlite_concurrency.py',
            'tests/test_production_setup.py', 'tests/test_validation_command.py',
        }
        assert command[:3] == [validation.sys.executable, '-m', 'pytest']
        base_temp = Path(command[command.index('--basetemp') + 1])
        assert base_temp == directory / 'pytest'
        assert not base_temp.exists()
        calls.append(directory)
        return SimpleNamespace(returncode=exit_code)

    monkeypatch.setattr(validation.subprocess, 'run', run)
    assert validation.main([]) == exit_code
    assert len(calls) == 1
    assert not calls[0].exists()
    assert validation.os.environ['DATABASE_URL'] == 'sqlite:///must-not-be-used.db'
    assert validation.os.environ['OPENAI_API_KEY'] == 'fake-key-not-for-use'


def test_validation_rejects_unreviewed_test_selection(validation):
    with pytest.raises(SystemExit) as error:
        validation.main(['tests/test_playwright_atendimento.py'])
    assert error.value.code == 2


def test_validation_works_without_access_to_default_pytest_temp(validation, monkeypatch, tmp_path):
    # Reproduce an unusable default temp root without changing Windows ACLs or
    # touching the user's pytest-of-* directory. A file cannot hold temp folders.
    unusable_default = tmp_path / 'unusable-default-root'
    unusable_default.write_text('This is a file, not a directory.', encoding='utf-8')
    monkeypatch.setenv('PYTEST_DEBUG_TEMPROOT', str(unusable_default))
    probe = tmp_path / 'test_temporary_probe.py'
    probe.write_text('def test_temporary_directory(tmp_path):\n    assert tmp_path.is_dir()\n',
                     encoding='utf-8')
    monkeypatch.setattr(validation, 'TEST_FILES', (str(probe),))
    # Use a real subprocess: the regression concerns pytest's actual tmp_path
    # initialization, not just how our command arguments are assembled.
    assert validation.main([]) == 0
    assert unusable_default.read_text(encoding='utf-8') == 'This is a file, not a directory.'

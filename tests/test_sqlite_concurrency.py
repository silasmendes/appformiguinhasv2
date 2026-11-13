"""Exercise independent connections against real files, never the user's data."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event

import pytest

from app import create_app, db


@pytest.fixture(params=['main', 'pre'])
def engine(request, tmp_path):
    app = create_app({
        'TESTING': True, 'ENV': 'development',
        'SQLALCHEMY_DATABASE_URI': f"sqlite:///{(tmp_path / 'main.db').as_posix()}",
        'SQLALCHEMY_PRE_CADASTRO_URI': f"sqlite:///{(tmp_path / 'pre.db').as_posix()}",
        'SESSION_FILE_DIR': str(tmp_path / 'sessions'),
        'SQLITE_BUSY_TIMEOUT_MS': 2000,
    })
    with app.app_context():
        engines = [db.engine, app.extensions['pre_cadastro_engine']]
        selected = engines[request.param == 'pre']
        with selected.begin() as conn:
            conn.exec_driver_sql('CREATE TABLE concurrent_updates (id INTEGER PRIMARY KEY, value INTEGER)')
            conn.exec_driver_sql('INSERT INTO concurrent_updates VALUES (1, 0)')
        try:
            yield selected
        finally:
            db.session.remove()
            for item in engines:
                item.dispose()


def test_policy_on_new_connections(engine):
    with engine.connect() as first, engine.connect() as second:
        for conn in (first, second):
            assert conn.exec_driver_sql('PRAGMA journal_mode').scalar() == 'wal'
            assert conn.exec_driver_sql('PRAGMA busy_timeout').scalar() == 2000


def test_ten_concurrent_writers(engine):
    barrier = Barrier(10)

    def update(index):
        with engine.connect() as conn:
            barrier.wait(timeout=10)
            conn.exec_driver_sql('INSERT INTO concurrent_updates VALUES (?, ?)', (index + 2, index))
            conn.commit()

    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(update, range(10)))
    with engine.connect() as conn:
        assert conn.exec_driver_sql('SELECT count(*) FROM concurrent_updates').scalar() == 11


def test_reader_and_waiting_writer_during_write(engine):
    attempted = Event()
    finished = Event()

    def waiting_writer():
        with engine.begin() as conn:
            attempted.set()
            conn.exec_driver_sql('UPDATE concurrent_updates SET value = value + 1 WHERE id = 1')
        finished.set()

    # Open all connections before taking the lock to test write contention itself.
    with ThreadPoolExecutor(max_workers=1) as executor, engine.connect() as writer:
        writer.exec_driver_sql('UPDATE concurrent_updates SET value = 10 WHERE id = 1')
        with engine.connect() as reader:
            assert reader.exec_driver_sql('SELECT value FROM concurrent_updates WHERE id = 1').scalar() == 0
        future = executor.submit(waiting_writer)
        assert attempted.wait(timeout=5)
        assert not finished.wait(timeout=0.15)
        writer.commit()
        future.result(timeout=5)
    with engine.connect() as conn:
        assert conn.exec_driver_sql('SELECT value FROM concurrent_updates WHERE id = 1').scalar() == 11

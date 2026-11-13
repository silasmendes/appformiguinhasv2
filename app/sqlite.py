"""Connection policy shared by the application's SQLite engines."""
from sqlalchemy import event


def configure_sqlite(engine, timeout_ms):
    if engine.dialect.name != 'sqlite':
        return
    timeout_ms = int(timeout_ms)
    if not 0 < timeout_ms <= 2147483647:
        raise ValueError('SQLITE_BUSY_TIMEOUT_MS deve ser um inteiro positivo de 32 bits.')

    @event.listens_for(engine, 'connect')
    def configure_connection(connection, _record):
        cursor = connection.cursor()
        try:
            cursor.execute(f'PRAGMA busy_timeout = {timeout_ms}')
            mode = cursor.execute('PRAGMA journal_mode = WAL').fetchone()[0]
            # In-memory databases cannot use WAL.
            if mode.lower() not in ('wal', 'memory'):
                raise RuntimeError(f'Não foi possível ativar WAL: {mode}')
        finally:
            cursor.close()

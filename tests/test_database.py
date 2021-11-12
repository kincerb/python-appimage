import os
import sqlite3
import sys
from contextlib import contextmanager
from pytest import fixture

DATA = ('Frodo Baggins', 33, '3f6i')


@contextmanager
def db_conn(*args, **kwargs):
    conn = sqlite3.connect('memory')
    yield conn


@fixture(scope='session')
def database_conn():
    with db_conn() as conn:
        cur = conn.cursor()
        yield cur
        conn.close()
        os.remove('memory')


@fixture(scope='session')
def database(database_conn):
    database_conn.execute('''
                            CREATE TABLE shirelings (
                            name varchar(255),
                            age int,
                            height int
                            )
                          ''')
    database_conn.execute(f"INSERT INTO shirelings VALUES {DATA}")
    yield database_conn


def test_version(database):
    database.execute('SELECT 1,SQLITE_VERSION()')
    data = database.fetchone()
    assert data[1] == '3.35.1'


def test_read(database):
    database.execute('SELECT * FROM shirelings')
    data = database.fetchone()
    assert data == DATA
    assert isinstance(data[0], str)
    assert isinstance(data[1], int)


def test_sqlite_tests_work(host):
    cmd = host.run(f'{sys.executable} -m test test_sqlite')
    assert cmd.succeeded

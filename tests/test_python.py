import ssl
import subprocess
import sys


def test_python_can_import(host):
    cmd = host.run(f"{sys.executable} -c 'import ssl, sqlite3, math'")
    assert cmd.succeeded


def test_ssl_version():
    assert ssl.OPENSSL_VERSION.split()[1] == '1.1.1k'


def test_ssl_create_context():
    assert isinstance(ssl.create_default_context(), ssl.SSLContext)


def test_ssl_certificate():
    context = ssl.create_default_context()
    assert context.load_verify_locations('./resources/cert.pem') is None


def test_ssl_tests_work(host):
    cmd = host.run(f'{sys.executable} -m test test_ssl')
    assert cmd.succeeded


def test_curses_tests_work(host):
    cmd = host.run(f'{sys.executable} -m test -ucurses test_curses')
    assert cmd.succeeded


def test_subprocess_can_run():
    output = subprocess.run(['ls'], capture_output=True)
    assert isinstance(output, subprocess.CompletedProcess)
    assert output.returncode == 0

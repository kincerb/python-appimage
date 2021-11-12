#!/usr/bin/env python3
import argparse
import logging
import logging.config
import logging.handlers
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Union

PROJECT_DIR = Path().absolute()


class AppImageError(Exception):
    """Custom exception for any error related to building the AppImage."""
    pass


def main():
    args = get_args()
    args.source_dir = Path(args.source_dir).expanduser().absolute()
    args.resources_dir = Path(args.resources_dir).expanduser().absolute()
    configure_logging(verbosity=args.verbosity)

    source_config = get_source_configs(args.source_dir)
    if source_config['cpython']['source_path'] is None:
        logging.critical(f'cpython source not found in {args.source_dir}')
        sys.exit(1)

    with TemporaryDirectory() as work_dir:
        app_dir = Path(work_dir, 'AppDir')
        logging.debug(f'Temp directory is {app_dir}')
        build_app_dir(app_dir)
        try:
            configure_sqlite(source_config['sqlite'], app_dir)
            configure_openssl(source_config['openssl'], app_dir)
            python_version = configure_python(source_config['cpython'], app_dir)
            add_venv_module(app_dir, args.source_dir, python_version)
            build_app_image(app_dir, args.resources_dir)
        except AppImageError as e:
            logging.critical(e)
            sys.exit(2)


def add_venv_module(app_dir: Path, source_dir: Path, version: str) -> None:
    """Copy venv module into the base python.

    :param app_dir: Base AppDir directory
    :type app_dir: Path
    :param source_dir: Directory that contains all source code
    :type source_dir: Path
    :param version: Python version
    :type version: str
    :raises AppImageError: Copying failed
    """
    release = '.'.join(version.split('.')[:2])
    module_dir = app_dir.joinpath('usr', 'local', 'lib', f'python{release}', 'appimage_venv')
    logging.debug(f'Copying appimage_venv module to {module_dir}')
    try:
        shutil.copytree(source_dir.joinpath('appimage_venv'), module_dir)
        make_readable(module_dir)
    except (shutil.Error, AppImageError) as e:
        raise(AppImageError(e))


# noinspection PyTypedDict
def get_source_configs(source_dir: Path) -> dict:
    """Returns tuple of filenames for sqlite, openssl, and python sources.

    :param source_dir: Directory that contains all source code
    :type source_dir: Path
    :returns: Source configs as a dictionary
    :rtype: dict
    """
    source_config = {
        'cpython': {
            'source_path': None,
            'version': None,
        },
        'openssl': {
            'source_path': None,
            'version': None,
        },
        'sqlite': {
            'source_path': None,
            'version': None,
        },
    }

    for _entry in source_dir.iterdir():
        if _entry.match('sqlite*.tar.gz'):
            source_config['sqlite']['source_path'] = _entry
            source_config['sqlite']['version'] = get_version_from_filename(_entry)
            continue
        if _entry.match('openssl*.tar.gz'):
            source_config['openssl']['source_path'] = _entry
            source_config['openssl']['version'] = get_version_from_filename(_entry)
            continue
        if _entry.match('cpython*.tar.gz'):
            source_config['cpython']['source_path'] = _entry
            continue

    logging.debug(f'source_config: {source_config}')
    return source_config


def get_version_from_filename(filename: Path) -> Union[str, None]:
    """Returns version as string or None from filename of source tarball.

    :param filename: Path object pointing to source tarball
    :type filename: Path
    :returns: version as a string, or None
    :rtype: Union[str, None]
    """
    if '-' not in filename.name:
        return None

    _version = filename.name.split('-', 2)[-1]
    return _version.replace('.tar.gz', '')


def run_command(command: str) -> str:
    """Run a command and return the output.

    :param command: Command to run
    :type command: str
    :returns: The completed process output
    :rtype: str
    :raises AppImageError: Command failed
    """
    command = ' '.join(command.split())
    logging.debug(f'Running {command}')
    result = subprocess.run(command, capture_output=True, shell=True)

    if result.returncode != 0:
        raise AppImageError(result.stderr.decode())

    return result.stdout.decode()


def build_app_dir(directory: Path) -> None:
    """Build the AppDir directory structure.

    :param directory: Path object to AppDir
    :type directory: Path
    """
    for _target in ['src', 'usr']:
        try:
            directory.joinpath(_target).mkdir(parents=True)
        except FileExistsError:
            logging.info(f'AppDir/{directory} directory already exists')


def make_readable(directory: Path) -> None:
    """Make libraries readable by everyone (linkable)

    :param directory: Directory to traverse
    :type directory: Path
    """
    try:
        run_command(f'find {directory} -type d -exec chmod o+rx {{}} \;')  # noqa: W605
        run_command(f'find {directory} -type f -exec chmod o+r {{}} \;')  # noqa: W605
    except AppImageError as e:
        logging.warning(e)


def configure_sqlite(sqlite_config: dict, app_dir: Path) -> None:
    """Configure and compile sqlite source.

    :param sqlite_config: Dictionary of sqlite config
    :type sqlite_config: dict
    :param app_dir: Path object pointing to AppDir
    :type app_dir: Path
    :raises AppImageError: Compiling sqlite failed
    """
    logging.info('Compiling and installing sqlite.')
    target_directory = app_dir.joinpath('src')
    version = sqlite_config.get('version')
    unpacked_directory = target_directory.joinpath(f'sqlite-autoconf-{version}')
    source_file = sqlite_config.get('source_path')
    shutil.unpack_archive(str(source_file), str(target_directory))
    os.chdir(unpacked_directory)

    try:
        run_command('./configure --prefix=/usr/local/sqlite3')
        run_command('make -j$(nproc)')
        run_command(f'make install DESTDIR={app_dir}')
        make_readable(app_dir.joinpath('usr', 'local', 'sqlite3'))
    except AppImageError:
        raise
    finally:
        os.chdir(PROJECT_DIR)
        shutil.rmtree(str(unpacked_directory))


def configure_openssl(openssl_config: dict, app_dir: Path) -> None:
    """Configure and compile openssl source.

    :param openssl_config: Dictionary of sqlite config
    :type openssl_config: dict
    :param app_dir: Path object pointing to AppDir
    :type app_dir: Path
    :raises AppImageError: Compiling ssl failed
    """
    logging.info('Compiling and installing openssl.')
    target_directory = app_dir.joinpath('src')
    version = openssl_config.get('version')
    unpacked_directory = target_directory.joinpath(f'openssl-{version}')
    source_file = openssl_config.get('source_path')
    shutil.unpack_archive(str(source_file), str(target_directory))
    os.chdir(unpacked_directory)

    try:
        run_command('./config \
                     no-shared \
                     -fPIC \
                     --prefix=/usr/local/ssl \
                     --openssldir=/usr/local/ssl')
        run_command('make -j$(nproc)')
        run_command(f'make install DESTDIR={app_dir}')
        make_readable(app_dir.joinpath('usr', 'local', 'ssl'))
    except AppImageError:
        raise
    finally:
        os.chdir(PROJECT_DIR)
        shutil.rmtree(str(unpacked_directory))


def configure_python(python_config: dict, app_dir: Path) -> str:
    """Configure and compile python source.

    :param python_config: Dictionary of python config
    :type python_config: dict
    :param app_dir: Path object pointing to AppDir
    :type app_dir: Path
    :returns: Python version compiled
    :rtype: str
    :raises AppImageError: Compiling python failed
    """
    logging.info('Compiling and installing python.')
    target_directory = app_dir.joinpath('src')
    source_file = python_config.get('source_path')
    shutil.unpack_archive(str(source_file), str(target_directory))
    version = None

    for _entry in target_directory.glob('cpython*'):
        if _entry.is_dir():
            version = get_version_from_filename(_entry)
            break
    if version is None:
        raise AppImageError('Could not determine unpacked cpython directory.')

    unpacked_directory = target_directory.joinpath(f'cpython-{version}')
    ld_flags = f'-Wl,-rpath={app_dir}/usr/local/sqlite3/lib,-rpath={app_dir}/usr/local/ssl/lib'
    cpp_flags = f'-I{app_dir}/usr/local/sqlite3/include -I{app_dir}/usr/local/ssl/include'

    os.chdir(unpacked_directory)

    try:
        py_install = run_command(f'export LDFLAGS="{ld_flags}" && \
                                   export CPPFLAGS="{cpp_flags}" && \
                                   ./configure \
                                   --with-pydebug \
                                   --enable-loadable-sqlite-extensions \
                                   --with-openssl={app_dir}/usr/local/ssl \
                                   --prefix=/usr/local')
        logging.debug(py_install)
        run_command('make -j$(nproc)')
        run_command(f'make install DESTDIR={app_dir}')
        return version
    except AppImageError:
        raise
    finally:
        os.chdir(PROJECT_DIR)
        shutil.rmtree(str(unpacked_directory))


def build_app_image(app_dir: Path, resources_dir: Path) -> None:
    """Build the AppImage.

    :param app_dir: Base AppDir directory
    :type app_dir: Path
    :param resources_dir: Directory that contains the resources
    :type resources_dir: Path
    :raises AppImageError: Creating AppImage failed
    """
    logging.info('Building AppImage.')
    icon_file = resources_dir.joinpath('icons', 'python.png')
    desktop_file = resources_dir.joinpath('io.nucoder.python.desktop')
    app_run_file = resources_dir.joinpath('AppRun')
    shutil.copy(app_run_file, app_dir)
    app_dir.joinpath('AppRun').chmod(0o755)

    libraries = get_system_libraries()

    try:
        run_command(f'ARCH=x86_64 OUTPUT=python3.10.0.AppImage \
                      {resources_dir}/linuxdeploy-x86_64.AppImage \
                      {libraries} \
                      --appdir={app_dir} \
                      --icon-file={icon_file} \
                      --desktop-file={desktop_file} \
                      --output=appimage')
    except AppImageError:
        raise


def get_system_libraries() -> str:
    """Return string of library flags to pass to linuxdeploy.

    :returns: String of flags
    :rtype: str
    """
    linux_distro = get_linux_distro()
    if linux_distro == 'Debian':
        # debian 10
        return '--library=/lib/x86_64-linux-gnu/libreadline.so.7 \
                --library=/lib/x86_64-linux-gnu/libhistory.so.7 \
                --library=/lib/x86_64-linux-gnu/libncurses.so.6 \
                --library=/lib/x86_64-linux-gnu/libncursesw.so.6'
    elif linux_distro == 'Ubuntu':
        # ubuntu 20.04
        return '--library=/lib/x86_64-linux-gnu/libreadline.so.8 \
                --library=/lib/x86_64-linux-gnu/libhistory.so.8 \
                --library=/lib/x86_64-linux-gnu/libncurses.so.6 \
                --library=/lib/x86_64-linux-gnu/libncursesw.so.6'
    else:
        # centos 7
        return '--library=/lib64/libreadline.so.6 \
                --library=/lib64/libhistory.so.6 \
                --library=/lib64/libncurses.so.5 \
                --library=/lib64/libncursesw.so.5'


def get_linux_distro() -> str:
    """Return distro as string.

    :returns: Distro name
    :rtype: str
    """
    pretty_linux_distro = run_command("cat /etc/*-release | head -1")
    if "Debian" in pretty_linux_distro:
        return "Debian"
    elif "CentOS" in pretty_linux_distro:
        return "CentOS"
    elif any([_distro in pretty_linux_distro for _distro in ['Ubuntu', 'Pop']]):
        return "Ubuntu"
    return "CentOS"


def get_args() -> argparse.Namespace:
    """Parse arguments passed at invocation.

    Returns:
        argparse.Namespace: Parsed argument namespace.
    """
    parser = argparse.ArgumentParser(
        description='Python AppImage builder',
        epilog='Example: %(prog)s'
    )
    parser.add_argument('source_dir', help='Path to sources directory')
    parser.add_argument('resources_dir', help='Path to resources directory')
    parser.add_argument('-v', '--verbose',
                        required=False,
                        dest='verbosity',
                        action='count',
                        default=0,
                        help='Increase output verbosity.')
    return parser.parse_args()


def configure_logging(verbosity=0) -> None:
    """Configures logging in the globally defined logging object.

    Args:
        verbosity (int, optional): Increment to increase verbosity.
        Defaults to 0.

    Returns:
        None
    """
    level = 'INFO' if verbosity == 0 else 'DEBUG'
    config = {
        'version': 1,
        'disable_existing_loggings': False,
        'formatters': {
            'console': {
                'format': '%(levelname)-8s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'console',
            }
        },
        'loggers': {
            'root': {
                'level': level,
                'handlers': ['console'],
                'propagate': False
            }
        }
    }
    logging.config.dictConfig(config)


if __name__ == '__main__':
    PROJECT_DIR = Path(__file__).parent.absolute()
    main()

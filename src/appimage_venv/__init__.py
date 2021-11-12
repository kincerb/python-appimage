"""AppImage wrapper module for creating virtual environments with the venv
module."""
import logging
import os
import sys
from pathlib import Path
from venv import EnvBuilder
from types import SimpleNamespace

CORE_VENV_DEPS = ('pip', 'setuptools')
logger = logging.getLogger(__name__)

try:
    APPIMAGE_PATH = os.environ['APPIMAGE']
except KeyError:
    print('Error: This wrapper is meant to be ran by an AppImage.')
    print("Error: Environment variable 'APPIMAGE' not found.")
    sys.exit(2)


class AppImageEnvBuilder(EnvBuilder):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def modify_venv(self, env_dir: str) -> None:
        """Modify venv that has been created to run properly from an
        AppImage."""
        context = self.get_venv_context(env_dir)
        self.modify_symlink(context)
        self.modify_pyvenvcfg(context)
        self.modify_scripts(context)
        self.write_pipconf(context)

    def get_venv_context(self, env_dir: str) -> SimpleNamespace:
        """Returns a context object that holds paths required for modifying the
        Venv to be used with an AppImage.

        Consequently to get the original context,
        EnvBuilder.ensure_directories is called. This shouldn't pose a
        problem because the environment was just created, but beware
        this is a side-effect.
        """
        context = self.ensure_directories(env_dir)
        context.env_dir = os.path.abspath(env_dir)
        executable = APPIMAGE_PATH
        dirname, exename = os.path.split(os.path.abspath(executable))
        context.executable = executable
        context.python_dir = dirname
        context.python_exe = exename
        context.bin_full_path = os.path.abspath(context.bin_path)
        context.lib_path = os.path.join(
            context.env_dir, 'lib', 'python%d.%d' % sys.version_info[:2], 'site-packages'
        )
        return context

    @staticmethod
    def modify_symlink(context: SimpleNamespace):
        """Move symlink to AppImage python."""
        python_symlink = Path(context.env_exe)
        python_symlink.unlink()
        python_symlink.symlink_to(context.executable)

    @staticmethod
    def modify_pyvenvcfg(context: SimpleNamespace):
        """Modify pyvenv.cfg to have proper home setting.

        Due to the small size of the file, let's just read the file into
        memory.
        """
        pyvenvcfg = Path(context.env_dir).joinpath('pyvenv.cfg')
        with pyvenvcfg.open(mode='r') as f:
            _lines = f.readlines()

        for _index, _line in enumerate(_lines):
            if _line.startswith('home ='):
                _lines[_index] = f'home = {context.executable}\n'

        with pyvenvcfg.open(mode='w') as f:
            f.writelines(_lines)

    def modify_scripts(self, context: SimpleNamespace):
        """Rewrite the scripts in $VENV/bin to add vars needed for AppImage."""
        for _script in ('activate', 'activate.csh', 'activate.fish'):
            _template = Path(__file__).absolute().parent.joinpath('scripts', _script)
            _destination = Path(context.bin_path).joinpath(_script)
            with _template.open(mode='r') as _in, _destination.open(mode='w') as _out:
                for _in_line in _in:
                    _out_line = self.replace_text(_in_line, context)
                    _out.write(_out_line)
        windows_activate = Path(context.bin_path).joinpath('Activate.ps1')
        windows_activate.unlink(missing_ok=True)

    def write_pipconf(self, context: SimpleNamespace):
        """Write out pip.conf in the root of the $VENV."""
        _template = Path(__file__).absolute().parent.joinpath('configs', 'pip.conf')
        _destination = Path(context.env_dir).joinpath('pip.conf')
        with _template.open(mode='r') as _in, _destination.open(mode='w') as _out:
            for _in_line in _in:
                _out_line = self.replace_text(_in_line, context)
                _out.write(_out_line)

    @staticmethod
    def replace_text(line: str, context: SimpleNamespace) -> str:
        """Helper method to replace common text in string."""
        line = line.replace('__VENV_DIR__', context.env_dir)
        line = line.replace('__VENV_LIB_DIR__', context.lib_path)
        line = line.replace('__VENV_BIN_NAME__', context.bin_full_path)
        line = line.replace('__VENV_PROMPT__', context.prompt)
        return line


def create(env_dir, system_site_packages=False, clear=False,
           symlinks=False, with_pip=False, prompt=None, upgrade_deps=False):
    """Create a virtual environment in a directory."""
    builder = AppImageEnvBuilder(
        system_site_packages=system_site_packages,
        clear=clear, symlinks=symlinks, with_pip=with_pip,
        prompt=prompt, upgrade_deps=upgrade_deps
    )
    builder.create(env_dir)
    builder.modify_venv(env_dir)


def main(args=None):
    compatible = True
    if sys.version_info < (3, 3):
        compatible = False
    elif not hasattr(sys, 'base_prefix'):
        compatible = False
    if not compatible:
        raise ValueError('This script is only for use with Python >= 3.3')
    else:
        import argparse

        parser = argparse.ArgumentParser(prog=__name__,
                                         description='Creates virtual Python '
                                                     'environments in one or '
                                                     'more target '
                                                     'directories.',
                                         epilog='Once an environment has been '
                                                'created, you may wish to '
                                                'activate it, e.g. by '
                                                'sourcing an activate script '
                                                'in its bin directory.')
        parser.add_argument('dirs', metavar='ENV_DIR', nargs='+',
                            help='A directory to create the environment in.')
        parser.add_argument('--system-site-packages', default=False,
                            action='store_true', dest='system_site',
                            help='Give the virtual environment access to the '
                                 'system site-packages dir.')
        if os.name == 'nt':
            use_symlinks = False
        else:
            use_symlinks = True
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--symlinks', default=use_symlinks,
                           action='store_true', dest='symlinks',
                           help='Try to use symlinks rather than copies, '
                                'when symlinks are not the default for '
                                'the platform.')
        group.add_argument('--copies', default=not use_symlinks,
                           action='store_false', dest='symlinks',
                           help='Try to use copies rather than symlinks, '
                                'even when symlinks are the default for '
                                'the platform.')
        parser.add_argument('--clear', default=False, action='store_true',
                            dest='clear', help='Delete the contents of the '
                                               'environment directory if it '
                                               'already exists, before '
                                               'environment creation.')
        parser.add_argument('--upgrade', default=False, action='store_true',
                            dest='upgrade', help='Upgrade the environment '
                                                 'directory to use this version '
                                                 'of Python, assuming Python '
                                                 'has been upgraded in-place.')
        parser.add_argument('--without-pip', dest='with_pip',
                            default=True, action='store_false',
                            help='Skips installing or upgrading pip in the '
                                 'virtual environment (pip is bootstrapped '
                                 'by default)')
        parser.add_argument('--prompt',
                            help='Provides an alternative prompt prefix for '
                                 'this environment.')
        parser.add_argument('--upgrade-deps', default=False, action='store_true',
                            dest='upgrade_deps',
                            help='Upgrade core dependencies: {} to the latest '
                                 'version in PyPI'.format(' '.join(CORE_VENV_DEPS)))
        options = parser.parse_args(args)
        if options.upgrade and options.clear:
            raise ValueError('you cannot supply --upgrade and --clear together.')
        builder = AppImageEnvBuilder(
            system_site_packages=options.system_site,
            clear=options.clear,
            symlinks=options.symlinks,
            upgrade=options.upgrade,
            with_pip=options.with_pip,
            prompt=options.prompt,
            upgrade_deps=options.upgrade_deps)
        for d in options.dirs:
            builder.create(d)
            builder.modify_venv(d)


if __name__ == '__main__':
    rc = 1
    try:
        main()
        rc = 0
    except Exception as e:
        print('Error: %s' % e, file=sys.stderror)
    sys.exit(rc)

# This file must be used with "source bin/activate.csh" *from csh*.
# You cannot run it directly.
# Created by Davide Di Blasi <davidedb@gmail.com>.
# Ported to Python 3.3 venv by Andrew Svetlov <andrew.svetlov@gmail.com>

alias deactivate 'test $?_OLD_VIRTUAL_PATH != 0 && setenv PATH "$_OLD_VIRTUAL_PATH" && unset _OLD_VIRTUAL_PATH; rehash; test $?_OLD_VIRTUAL_PROMPT != 0 && set prompt="$_OLD_VIRTUAL_PROMPT" && unset _OLD_VIRTUAL_PROMPT; \
unsetenv VIRTUAL_ENV; test $?_OLD_PIP_CONFIG_FILE != 0 && setenv PIP_CONFIG_FILE "$_OLD_PIP_CONFIG_FILE" && unsetenv _OLD_PIP_CONFIG_FILE; \
test $?_OLD_PYTHONPATH != 0 && setenv PYTHONPATH "$_OLD_PYTHONPATH" && unsetenv _OLD_PYTHONPATH; test "\!:*" != "nondestructive" && unalias deactivate'

# Unset irrelevant variables.
deactivate nondestructive

setenv VIRTUAL_ENV "__VENV_DIR__"

set _OLD_PIP_CONFIG_FILE="$PIP_CONFIG_FILE"
setenv PIP_CONFIG_FILE "$VIRTUAL_ENV/pip.conf"

set _OLD_PYTHONPATH="$PYTHONPATH"
setenv PYTHONPATH="__VENV_LIB_DIR__"

set _OLD_VIRTUAL_PATH="$PATH"
setenv PATH "__VENV_BIN_NAME__:$PATH"

set _OLD_VIRTUAL_PROMPT="$prompt"

if (! "$?VIRTUAL_ENV_DISABLE_PROMPT") then
    set prompt = "__VENV_PROMPT__$prompt"
endif

alias pydoc python -m pydoc

rehash

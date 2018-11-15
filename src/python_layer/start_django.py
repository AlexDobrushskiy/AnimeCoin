#!/usr/bin/env python
import os
import sys

from core_modules.settings import NetWorkSettings

if __name__ == '__main__':
    # add django root folder to path
    sys.path.append(NetWorkSettings.DJANGO_ROOT)

    # parse arguments
    argv0, http_port, pastel_basedir, patel_rpc_ip, pastel_rpc_port, pastel_rpc_pubkey = sys.argv

    os.environ["PASTEL_BASEDIR"] = pastel_basedir
    os.environ["PASTEL_RPC_IP"] = patel_rpc_ip
    os.environ["PASTEL_RPC_PORT"] = pastel_rpc_port
    os.environ["PASTEL_RPC_PUBKEY"] = pastel_rpc_pubkey

    # vvvvv this code is from the original manage.py vvvvv
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # we modify the function call to run the server
    execute_from_command_line([argv0, "runserver", http_port])

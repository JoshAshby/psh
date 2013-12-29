#!/usr/bin/env python2
"""Psh Spinner Daemon

Usage:
  spinner.py start [-d | --daemon]
  spinner.py stop
  spinner.py restart
  spinner.py --version
  spinner.py (-h | --help)


Options:
  --help -h      Show this
  --daemon -d    Start the spinner as a daemon

"""
from config.rough import rough_parse_config, setup_log
from daemons.simpleDaemon import Daemon
from docopt import docopt


def run(self):
    setup_log("spinner")
    from daemons.spinner.spinner import Spinner

    spinner = Spinner()
    spinner.start()


if __name__ == "__main__":
    config = rough_parse_config("spinner")
    arguments = docopt(__doc__, version='Psh Spinner Daemon v0.1.0')

    if arguments["--daemon"] or arguments["stop"] or arguments["restart"]:
        AppDaemon = type('AppDaemon', (Daemon,), {"run": run})
        app = AppDaemon(config["files"]["pid"], stderr=config["files"]["stderr"])
    else:
        App = type('App', (), {"start": run})
        app = App()

    if arguments["start"]:
        app.start()

    if arguments["stop"]:
        app.stop()

    if arguments["restart"]:
        app.restart()

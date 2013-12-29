#!/usr/bin/env python2
"""Psh Builder Daemon

Usage:
  builder.py start [-d | --daemon]
  builder.py stop
  builder.py restart
  builder.py --version
  builder.py (-h | --help)


Options:
  --help -h      Show this
  --daemon -d    Start the builder as a daemon

"""
from config.rough import rough_parse_config, setup_log
from daemons.simpleDaemon import Daemon
from docopt import docopt


def run(self):
    setup_log("builder")
    from daemons.builder.builder import Builder

    builder = Builder()
    builder.start()


if __name__ == "__main__":
    config = rough_parse_config("builder")
    arguments = docopt(__doc__, version='Psh Builder Daemon v0.1.0')

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

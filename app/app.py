#!/usr/bin/env python2
"""Seshat

Usage:
  app.py start [-d | --daemon]
  app.py stop
  app.py restart
  app.py --version
  app.py (-h | --help)


Options:
  --help -h      Show this
  --daemon -d    Start Seshat as a daemon

"""
from config.rough import rough_parse_config, setup_log
from daemons.simpleDaemon import Daemon
from docopt import docopt


def run(self):
    setup_log()
    import seshat.framework as fw
    __import__("controllers.controllerMap", globals(), locals())

    fw.serveForever()


if __name__ == "__main__":
    config = rough_parse_config()
    arguments = docopt(__doc__, version='Seshat v1.0.0')

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

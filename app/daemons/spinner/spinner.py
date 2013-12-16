#!/usr/bin/env python
"""
For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import docker
import json
import logging
import random

import config.config as c

from models.rethink.container import containerModel as cm

import utils.pushover as ps
import utils.nginx as nu

logger = logging.getLogger(c.spinner.log_name)


class Spinner(object):
    def __init__(self):
        pass

    def start(self):
        try:
            logger.info("Starting up spin worker...")
            self.poll()
        except KeyboardInterrupt:
            logger.info("Keyboard shutdown")

    def poll(self):
        while True:
            next_json = c.redis.blpop("spin:queue")[1]

            next_parsed = json.loads(next_json)

            log = "Got Container doc id: {id} with action {action}".format(**next_parsed)
            logger.info(log)

            self.container = cm.Container(next_parsed["id"])

            if next_parsed["action"] == "build":
                self.build_container()

            elif next_parsed["action"] == "start":
                self.start_container()

            elif next_parsed["action"] == "restart":
                self.restart_container()

            elif next_parsed["action"] == "stop":
                self.stop_container()

    def build_container(self):
        image_id = self.container.image.docker_id

        ports = self.container.ports.keys()

        try:
            container_id = c.docker.create_container(image=image_id,
                                                     ports=ports,
                                                     hostname=self.container.hostname)["Id"]

            self.container.docker_id = container_id
            self.container.save()

            self.start_container()

        except c.docker.client.APIError as e:
            logger.error(e)

    def start_container(self):
        bindings = {}
        for port, options in self.container.ports.iteritems():
            if not "internal" in options or not options["internal"]:
                bindings[port] = random.randint(1025, 65535)

        success = False
        error = None
        while not success and not error:
            try:
                c.docker.start(self.container.docker_id, port_bindings=bindings)
                success = True

                logger.info("Container started: "+self.container.id)
                for con_port, host_port in bindings.iteritems():
                    self.container.ports[con_port]["internal"] = host_port

                self.container.save()
                nu.container_nginx_config(self.container)

            except docker.client.APIError as e:
                if e.is_client_error():
                    error = e
                    logger.error(e)
                if e.is_server_error():
                    # This still has a chance to fail
                    msg = e.explanation.rsplit(":", 1)
                    bad_port = int(msg)

                    for port in bindings:
                        if bindings[port] == bad_port:
                            bindings[port] = random.randint(1025, 65535)


    def restart_container(self):
        self.stop_container()
        self.start_container()

    def stop_container(self):
        try:
            self.dc.stop(self.container.docker_id)
        except c.docker.client.APIError as e:
            logger.error(e)

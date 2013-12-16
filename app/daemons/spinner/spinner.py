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

            container = cm.Container(next_parsed["id"])

            if next_parsed["action"] == "build":
                self.build_container(container)

            elif next_parsed["action"] == "start":
                self.start_container(container)

            elif next_parsed["action"] == "restart":
                self.restart_container(container)

            elif next_parsed["action"] == "stop":
                self.stop_container(container)

    def build_container(self, container_model):
        image_id = container_model.image.docker_id

        ports = []
        for port, options in container_model.ports.iteritems():
            ports.append(port)

        container_id = c.docker.create_container(image=image_id,
                                                 ports=ports,
                                                 hostname=container_model.hostname)["Id"]

        container_model.docker_id = container_id
        container_model.save()

        self.start_container(container_model)

    def start_container(self, container_model):
        bindings = {}
        for port, options in container_model.ports.iteritems():
            if not "internal" in options or not options["internal"]:
                bindings[port] = random.randint(1025, 65535)

        success = False
        error = None
        while not success and not error:
            try:
                c.docker.start(container_model.docker_id, port_bindings=bindings)
                success = True
            except docker.client.APIError as e:
                print e
                if e.is_client_error():
                    error = e
                    logger.error(e)
                if e.is_server_error():
                    msg = e.explanation.rsplit(":", 1)
                    bad_port = int(msg)

                    for port in bindings:
                        if bindings[port] == bad_port:
                            bindings[port] = random.randint(1025, 65535)

        if not error:
            logger.info("Container started: "+container_model.id)
            for con_port, host_port in bindings.iteritems():
                container_model.ports[con_port]["internal"] = host_port

            container_model.save()

            nu.container_nginx_config(container_model)

    def restart_container(self, container_model):
        self.stop_container(self, container_model)
        self.start_container(self, container_model)

    def stop_container(self, container_model):
        self.dc.stop(container_model.docker_id)

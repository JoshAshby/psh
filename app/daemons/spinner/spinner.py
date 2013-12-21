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
import utils.hipache as hi

logger = logging.getLogger(c.spinner.log_name)


class Spinner(object):
    def __init__(self):
        self.container = None

    def start(self):
        try:
            logger.info("Starting up spin worker...")
            self.poll()
        except KeyboardInterrupt:
            logger.info("Keyboard shutdown")

    def poll(self):
        while True:
            next_json = c.redis.blpop(["spin:queue", "spin:command"])

            if next_json[0] == "spin:queue":
                next_json = next_json[1]

                next_parsed = json.loads(next_json)

                log = "Got Container doc id: {id} with action {action}"\
                    .format(**next_parsed)
                logger.debug(log)

                self.container = cm.Container(next_parsed["id"])

                if next_parsed["action"] == "build":
                    self.build_container()

                elif next_parsed["action"] == "start":
                    self.start_container()

                elif next_parsed["action"] == "restart":
                    self.restart_container()

                elif next_parsed["action"] == "stop":
                    self.stop_container()

            else:
                pass

    def build_container(self):
        try:
            container_id = c.docker.create_container(image=self.container.image.docker_id,
                                                     ports=self.container.ports,
                                                     hostname=self.container.name)["Id"]

            self.container.docker_id = container_id
            self.container.save()

            self.start_container()

        except docker.client.APIError as e:
            self.push_error(e)

    def start_container(self):
        bindings = self.container.ports
        for internal, external in self.container.ports.iteritems():
            if not external:
                bindings[internal] = random.randint(1025, 65535)

        success = False
        error = None
        while not success and not error:
            try:
                c.docker.start(self.container.docker_id,
                               port_bindings=bindings)

                logger.debug("Container started: "+self.container.id)

                self.container.ports = bindings
                self.container.save()
                hi.route_container_ports(self.container)

                success = True

            except docker.client.APIError as e:
                if e.is_client_error():
                    self.push_error(e)
                    error = True
                if e.is_server_error():
                    if "port" in e:
                        # This still has a chance to fail
                        msg = e.explanation.rsplit(":", 1)
                        bad_port = int(msg)

                        for port in bindings:
                            if bindings[port] == bad_port:
                                bindings[port] = random.randint(1025, 65535)
                    else:
                        self.push_error(e)
                        error = True

    def stop_container(self):
        try:
            c.docker.stop(self.container.docker_id)
            logger.debug("Container stoped: "+self.container.id)
        except docker.client.APIError as e:
            self.push_error(e)

    def restart_container(self):
        self.stop_container()
        self.start_container()

    def push_error(self, e):
        logger.error(e)

        c.redis.rpush("spin:errors", str(e))
        if c.redis.llen("spin:errors") > 500:
            c.redis.lpop("spin:errors")

        try:
            ps.pushover(message="Error with containter {id}. {error}"\
                .format(id=self.container.id[:11], error=str(e)),
                        title="Failed to stop container")
        except:
            pass

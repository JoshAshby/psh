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

from config.standard import StandardConfig

from parse import parse

import rethinkdb as r
from models.rethink.container import containerModel as cm

import redis

import utils.pushover as ps


class Spinner(object):
    def __init__(self, config):
        self.c = StandardConfig(**config)

        if not self.c:
            raise Exception("Could not load spinner_config.yaml!")

        r.connect(db=self.c["databases"]["rethink"]["db"]).repl()

        self.redis = redis.StrictRedis(self.c["databases"]["redis"]["URL"],
                                       db=self.c["databases"]["redis"]["db"])

        dc_url = ":".join([self.c["docker"]["url"], str(self.c["docker"]["port"])])
        self.dc = docker.Client(base_url=dc_url,
                                version=str(self.c["docker"]["version"]),
                                timeout=self.c["docker"]["timeout"])

        self.logger = logging.getLogger(self.c.log_name)

    def start(self):
        try:
            self.logger.info("Starting up spin worker...")
            self.poll()
        except KeyboardInterrupt:
            self.logger.info("Keyboard shutdown")
            pass

    def poll(self):
        while True:
            next_json = self.c.redis.blpop("spin:queue")[1]

            next_parsed = json.loads(next_json)

            log = "Got Container doc id: {id} with action {action}".format(next_parsed)
            self.logger.debug(log)

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
        for port in container_model.ports:
            ports.append(port["container_port"])

        container_id = self.dc.create_container(image=image_id,
                                                ports=ports,
                                                name=container_model.name,
                                                hostname=container_model.hostname)

        container_model.docker_id = container_id
        container_model.save()

    def start_container(self, container_model):
        bindings = {}
        for port in container_model.ports:
            bindings[port["container_port"]] = random.randint(1025, 500000)

        success = False
        while not success:
            try:
                self.dc.start(container_model.docker_id, bindings=bindings)
                success = True
            except docker.client.APIError as e:
                if e.is_server_error():
                    msg = e.explanation.rsplit(":", 1)
                    bad_port = int(msg)

                    for port in bindings:
                        if bindings[port] == bad_port:
                            bindings[port] = random.randint(1025, 500000)

    def restart_container(self, container_model):
        self.stop_container(self, container_model)
        self.start_container(self, container_model)

    def stop_container(self, container_model):
        self.dc.stop(container_model.docker_id)
        pass

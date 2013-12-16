#!/usr/bin/env python
"""
For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import os
import config.config as c
from models.rethink.image import imageModel as im

import tempfile
import cStringIO

import docker

import utils.pushover as ps
import utils.files as fu

import logging

logger = logging.getLogger(c.builder.log_name)


class Builder(object):
    def __init__(self):
        self.image = None
        self.image_tag = ""
        pass

    def start(self):
        try:
            logger.info("Starting up build worker...")
            self.poll()

        except KeyboardInterrupt:
            logger.info("Keyboard shutdown")

    def poll(self):
        while True:
            next_id = c.redis.blpop("build:queue")[1]
            logger.debug("Got Image document id: "+next_id)
            self.image = im.Image(next_id)
            self.image_tag = "/".join([self.image.user.username, self.image.name])
            self.image_tag = "-".join([self.image_tag, self.image.rev])

            self.build()

    def build(self):
        if not self.image.additional_files:
            self.from_dockerfile()
        else:
            self.from_package()

    def from_dockerfile(self):
        try:
            dockerfile = tempfile.TemporaryFile()
            dockerfile.write(self.image.dockerfile)
            dockerfile.seek(0)

            logger.debug("Building "+self.image.id)
            s, m = c.docker.build(fileobj=dockerfile, tag=self.image_tag, rm=True)

            self.successful_build(s, m)

        except docker.client.APIError as e:
            self.failed_build(e)

    def from_package(self, image_model):
        try:
            tmp = fu.TemporaryDirectory()
            path = os.path.abspath(tmp.tmp)

            dockerfile_path = "/".join([path, "Dockerfile"])
            fu.write_file_string(dockerfile_path, self.image.dockerfile)

            for add_file in self.image.additional_files:
                add_file_path = "/".join([path, add_file])
                buff = cStringIO.StringIO(self.image.additional_files[add_file])
                fu.write_file(add_file_path, buff)

            logger.debug("Building "+self.image.id+" in a temp dir")
            s, m = c.docker.build(path=path, tag=self.image_tag, rm=True)

            tmp.destroy()
            self.successful_build(s, m)

        except docker.client.APIError as e:
            self.failed_build(e)


    def failed_build(self, image_model, e):
        ps.pushover(message="Building of image {id} failed.".format(id=self.image.id[:11]),
                    title="Failed image build")
        logger.error(str(e))
        self.image.add_image("failed", log=str(e))

    def successful_build(self, s, m):
        img = c.docker.images(self.image_tag)[0]
        self.image.add_image("success", log=m, docker_id=img["Id"])
        logger.debug("Build for "+self.image.id+" done")

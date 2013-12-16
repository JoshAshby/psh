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

import utils.pushover as ps
import utils.files as fu

import logging

logger = logging.getLogger(c.builder.log_name)


class Builder(object):
    def __init__(self):
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
            image_model = im.Image(next_id)

            self.build(image_model)

    def build(self, image_model):
        tag = "/".join([image_model.user.username, image_model.name])

        if not image_model.additional_files:
            dockerfile = tempfile.TemporaryFile()
            dockerfile.write(image_model.dockerfile)
            dockerfile.seek(0)

            logger.info("Building "+image_model.id)
            s, m = c.docker.build(fileobj=dockerfile, tag=tag, rm=True)
        else:
            tmp = fu.TemporaryDirectory()
            path = os.path.abspath(tmp.tmp)

            dockerfile_path = "/".join([path, "Dockerfile"])
            fu.write_file_string(dockerfile_path, image_model.dockerfile)

            for add_file in image_model.additional_files:
                add_file_path = "/".join([path, add_file])
                buff = cStringIO.cStringIO(image_model.additional_files[add_file])
                fu.write_file(add_file_path, buff)

            logger.info("Building "+image_model.id+" in a temp dir")
            s, m = c.docker.build(path=path, tag=tag, rm=True)

            tmp.destroy()

        if s:
            img = c.docker.images(tag)[0]

            image_model.add_image("success", log=m, docker_id=img["Id"])

            logger.info("Build for "+image_model.id+" done")

        else:
            ps.pushover(message="Building of image {id} failed.".format(id=image_model.id[:11]),
                        title="Failed image build")

            logger.error(m)

            image_model.add_image("fail", log=m)

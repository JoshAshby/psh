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
from models.rethink.dockerfile import dockerfileModel as dfm
from models.rethink.image import imageModel as im
from models.rethink.user import userModel as um

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
            logger.debug("Got Dockerfile document id: "+next_id)
            dockerfile_model = dfm.Dockerfile(next_id)
            user = um.User(dockerfile_model.user)

            tag = "/".join([user.username, dockerfile_model.name])

            if not dockerfile_model.additional_files:
                dockerfile = tempfile.TemporaryFile()
                dockerfile.write(dockerfile_model.dockerfile)
                dockerfile.seek(0)

                logger.info("Building "+next_id)
                s, m = c.docker.build(fileobj=dockerfile, tag=tag, rm=True)
            else:
                tmp = fu.TemporaryDirectory()
                path = os.path.abspath(tmp.tmp)

                dockerfile_path = "/".join([path, "Dockerfile"])
                fu.write_file_string(dockerfile_path, dockerfile_model.dockerfile)

                for add_file in dockerfile_model.additional_files:
                    add_file_path = "/".join([path, add_file])
                    buff = cStringIO.cStringIO(dockerfile_model.additional_files[add_file])
                    fu.write_file(add_file_path, buff)

                logger.info("Building "+next_id+" in a temp dir")
                s, m = c.docker.build(path=path, tag=tag, rm=True)

                tmp.destroy()

            if s:
                imgs = c.docker.images(tag)

                if len(imgs):
                    img = imgs[0]

                    img_model = im.Image.new_image(user=user.id,
                                                   name=tag,
                                                   docker_id=img["Id"],
                                                   dockerfile=dockerfile_model.id,
                                                   log=m)

                    user.images.append(img_model.id)
                    user.save()

                    dockerfile_model.status = True
                    dockerfile_model.save()
                    logger.info("Build for "+next_id+" done, image "+img_model.id)
                else:
                    ps.pushover(message="Build for Dockerfile {id} is gone".format(id=dockerfile_model.id[:11]),
                                title="Missing Dockerfile build")

                    logger.error(m)

            else:
                ps.pushover(message="Building of Dockerfile {id} failed.".format(id=dockerfile_model.id[:11]),
                            title="Failed Dockerfile build")

                logger.error(m)
          # TODO: Fix shit because if this breaks...

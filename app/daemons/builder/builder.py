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

import rethinkdb as r
from models.rethink.dockerfile import dockerfileModel as dfm
from models.rethink.image import imageModel as im
from models.rethink.user import userModel as um

import redis
import tempfile

import utils.pushover as ps

from config.standard import StandardConfig

import logging


class Builder(object):
    def __init__(self, config):
        self.c = StandardConfig(**config)

        if not self.c:
            raise Exception("Could not load builder_config.yaml!")

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
            self.logger.info("Starting up build worker...")
            self.poll()
        except KeyboardInterrupt:
            self.logger.info("Keyboard shutdown")
            pass

    def poll(self):
        while True:
            next_id = self.redis.blpop("build:queue")[1]
            self.logger.debug("Got Dockerfile document id: "+next_id)
            dockerfile_model = dfm.Dockerfile(next_id)
            user = um.User(dockerfile_model.user)

            tag = "/".join([user.username, dockerfile_model.name])

            r.table(im.Image.table).filter({"name": tag}).update({"latest": False}).run()

            dockerfile = tempfile.TemporaryFile()
            dockerfile.write(dockerfile_model.dockerfile)
            dockerfile.seek(0)

            self.logger.info("Building "+next_id)
            s, m = self.dc.build(fileobj=dockerfile, tag=tag, rm=True)
            if s:
                imgs = self.dc.images(tag)

                if len(imgs):
                    img = imgs[0]

                    img_model = im.Image.new_image(user=user.id,
                                                   name=tag,
                                                   img=img["Id"],
                                                   dockerfile=dockerfile_model.id)

                    user.images.append(img_model.id)
                    user.save()

                    dockerfile_model.status = True
                    dockerfile_model.save()
                    self.logger.info("Build for "+next_id+" done, image "+img_model.id)
                else:
                    ps.pushover(message="Build for Dockerfile {id} is gone".format(id=dockerfile_model.id[:11]),
                                title="Missing Dockerfile build")

                    self.logger.error(m)

            else:
                ps.pushover(message="Building of Dockerfile {id} failed.".format(id=dockerfile_model.id[:11]),
                            title="Failed Dockerfile build")

                self.logger.error(m)
          # TODO: Fix shit because if this breaks...

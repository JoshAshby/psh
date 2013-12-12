"""
http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import json
import config.config as c

import docker
import arrow

from rethinkORM import RethinkModel
from models.rethink.image import imageModel as im
from models.rethink.user import userModel as um
from errors.general import \
      NotFoundError


class Container(RethinkModel):
    table = "containers"

    def finish_init(self):
        if not self._data:
            raise NotFoundError("Container was not found.")

        self._formated_created = ""
        self._user = None
        self._con = None
        self._image = None

    @classmethod
    def new_container(cls, user, name, img, ports):
        fi = cls.create(user=user,
                        created=arrow.utcnow().timestamp,
                        name=name,
                        image_id=img,
                        disable=False,
                        docker_id=None,
                        ports=ports)

        fi.queue_action("build")

        return fi

    @property
    def docker_container(self, no_cache=False):
        if not self._con or no_cache:
            containers = docker.containers(all=True)
            for container in containers:
                if container["Id"] == self.docker_id:
                    self._con = container

        if not self._con:
            raise NotFoundError("Container was not found in docker")

        return self._con

    def queue_action(self, action):
        data = json.dumps({"id": self.id, "action": action})
        c.general.redis.rpush("spin:queue", data)

    @property
    def formated_created(self, no_cache=False):
        if not self._formated_created or no_cache:
            self._formated_created = arrow.get(self.created).format("MM/DD/YYYY hh:mm")

        return self._formated_created

    @property
    def author(self, no_cache=False):
        if not self._user or no_cache:
            self._user = um.User(self.user)
        return self._user

    @property
    def image(self, no_cache=False):
        if not self._image or no_cache:
            self._image = im.Image(self.image_id)

        return self._image

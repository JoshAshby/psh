"""
http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import arrow
import json

import config.config as c
from utils.standard import StandardODM

from rethinkORM import RethinkModel
from models.rethink.user import userModel as um
from models.rethink.image import imageModel as im

import models.redis.hipache.hipacheModel as him

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
    def new_container(cls, user_id, name, image_id, domains, http_port):
        image = im.Image(image_id)
        ports = { port: None for port in image.ports }

        fi = cls.create(user_id=user_id,
                        image_id=image_id,
                        name=name,
                        http_port=http_port,
                        domains=domains,
                        ports=ports,
                        created=arrow.utcnow().timestamp,
                        disable=False,
                        docker_id=None)

        fi.queue_action("build")

        return fi

    def update_http_port(self, port, new_domains=None):
        if new_domains and new_domains != self.domains:
            him.remove_container_routes(self, new_domains)
            self.domains = new_domains

        self.http_port = port
        self.save()

        him.route_container_ports(self)

    def queue_action(self, action):
        data = json.dumps({"id": self.id, "action": action})
        c.redis.rpush("spin:queue", data)

    @property
    def docker(self, no_cache=False):
        if not self._con or no_cache:
            containers = c.docker.containers(all=True)
            for container in containers:
                if container["Id"] == self.docker_id:
                    self._con = StandardODM(**container)

        return self._con

    @property
    def status(self):
        if not self.docker:
            return "Queued"
        if not self.disable:
            return self.docker.Status
        else:
            return "Disabled"

    @property
    def formated_created(self, no_cache=False):
        if not self._formated_created or no_cache:
            self._formated_created = arrow.get(self.created).format(c.general.time_format)

        return self._formated_created

    @property
    def user(self, no_cache=False):
        if not self._user or no_cache:
            self._user = um.User(self.user_id)

        return self._user

    @property
    def image(self, no_cache=False):
        if not self._image or no_cache:
            self._image = im.Image(self.image_id)

        return self._image

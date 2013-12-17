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
    def new_container(cls, user_id, name, image_id, ports, hostname):
        """
        ports should be in the form of:
        {
          container_port: host
        }

        where host can be None or a number
        """
        port_bindings = {}
        for container, host in ports.iteritems():
            port_bindings[container] = {
                "host": host,
                "internal": None
            }

        fi = cls.create(user_id=user_id,
                        image_id=image_id,
                        name=name,
                        ports=port_bindings,
                        hostname=hostname,
                        created=arrow.utcnow().timestamp,
                        disable=False,
                        docker_id=None)

        fi.queue_action("build")

        return fi

    def update_ports(self, ports):
        port_bindings = {}
        for container, host in ports.iteritems():
            port_bindings[container] = {
                "host": host,
                "internal": self.ports[container]["internal"]
            }

        self.ports = port_bindings
        self.save()

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

        if not self._con:
            raise NotFoundError("Container was not found in docker")

        return self._con

    @property
    def status(self):
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

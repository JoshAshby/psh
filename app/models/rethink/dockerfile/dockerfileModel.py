"""

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
from rethinkORM import RethinkModel
import arrow

from errors.general import \
      ExistingError
from errors.general import \
      NotFoundError

import rethinkdb as r

from models.rethink.user import userModel as um
from models.rethink.image import imageModel as im

import config.config as c


class Dockerfile(RethinkModel):
    table = "dockerfiles"

    def finish_init(self):
        if not self._data:
            raise NotFoundError("User was not found.")
        self._formated_created = ""

    @classmethod
    def new_dockerfile(cls, user, name, file_obj, public=False, override=False):
        found = r.table(cls.table).filter({'name': name, 'user': user}).count().run()
        if not found or override:
            fi = cls.create(user=user,
                     dockerfile=unicode(file_obj.read()),
                     created=arrow.utcnow().timestamp,
                     name=name,
                     status=False,
                     public=public)

            u = um.User(user)
            u.dockerfiles.append(fi.id)
            u.save()

            c.general.redis.rpush("build:queue", fi.id)
            return fi

        else:
            raise ExistingError("Another Dockerfile of that name exists in the system.")

    @property
    def formated_created(self, no_cache=False):
        if not self._formated_created or no_cache:
            self._formated_created = arrow.get(self.created).format("MM/DD/YYYY hh:mm")

        return self._formated_created

    @property
    def author(self):
        return um.User(self.user).username

    @property
    def latest_image(self):
        img = r.table(im.Image.table).filter({"dockerfile": self.id, "latest": True}).coerce_to("array").run()
        if img:
            return img[0]["id"]
        else:
            return None

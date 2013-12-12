"""

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import rethinkdb as r
from rethinkORM import RethinkModel
import arrow

from models.rethink.user import userModel as um

from errors.general import \
      NotFoundError


class Image(RethinkModel):
    table = "images"

    def finish_init(self):
        if not self._data:
            raise NotFoundError("Image was not found.")
        self._formated_created = ""
        self._latest = None
        self._user = None

    @classmethod
    def new_image(cls, user, name, docker_id, dockerfile, log):
        found = r.table(cls.table).filter({'name': name, 'user': user}).count().run()

        fi = cls.create(user=user,
                        dockerfile=dockerfile,
                        created=arrow.utcnow().timestamp,
                        name=name,
                        docker_id=docker_id,
                        log=log,
                        rev=found+1,
                        disable=False)
        return fi

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
    def latest(self, no_cache=False):
        if not self._latest or no_cache:
            max_rev = r.table(self.table).filter({"dockerfile": self.dockerfile}).map(lambda user: user["rev"]).reduce(lambda left, right: r.branch(left>right,left,right)).run()

            img = r.table(self.table).filter({"dockerfile": self.dockerfile, "rev": max_rev}).pluck("id").coerce_to("array").run()
            if img and img[0]["id"] != self.id:
                self._latest = Image(img[0]["id"])

        return self._latest

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

import rethinkdb as r

from models.rethink.user import userModel as um


class Dockerfile(RethinkModel):
    table = "dockerfiles"

    def finish_init(self):
        self._formated_created = ""

    @classmethod
    def new_dockerfile(cls, userid, name, file_obj, public=False, override=False):
        found = r.table(cls.table).filter({'name': name, 'user': userid}).count().run()
        if not found or override:
            fi = cls.create(user=userid,
                     dockerfile=unicode(file_obj.read()),
                     created=arrow.utcnow().timestamp,
                     name=name,
                     status=False,
                     public=public)
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

"""

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
from rethinkORM import RethinkModel
import arrow

from models.rethink.user import userModel as um


class Image(RethinkModel):
    table = "images"

    def finish_init(self):
        self._formated_created = ""

    @classmethod
    def new_image(cls, user, name, img, dockerfile, log):
        fi = cls.create(user=user,
                        dockerfile=dockerfile,
                        created=arrow.utcnow().timestamp,
                        name=name,
                        img=img,
                        latest=True,
                        log=log)
        return fi


    @property
    def formated_created(self, no_cache=False):
        if not self._formated_created or no_cache:
            self._formated_created = arrow.get(self.created).format("MM/DD/YYYY hh:mm")

        return self._formated_created

    @property
    def author(self):
        return um.User(self.user).username

"""

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
from rethinkORM import RethinkModel
import arrow
import cStringIO

from errors.general import \
      NotFoundError, MissingError
import rethinkdb as r

from models.rethink.user import userModel as um
from models.rethink.image import imageModel as im

import config.config as c

import tarfile


class Dockerfile(RethinkModel):
    table = "dockerfiles"

    def finish_init(self):
        if not self._data:
            raise NotFoundError("Dockerfile was not found.")

        self._formated_created = ""
        self._ports = []
        self._latest = None
        self._latest_img = None
        self._user = None

    @classmethod
    def new_dockerfile(cls, user, name, file_obj, public=False, override=False):
        found = r.table(cls.table).filter({'name': name, 'user': user}).count().run()

        add_files = {}
        if not file_obj.extension:
            dockerfile = file_obj.read()

        elif file_obj.extension in ["tar", "tar.gz", "tar.bz2"]:
            dockerfile = None
            with tarfile.open(fileobj=file_obj.file) as tar:
                for entry in tar:
                    if entry.isfile():
                        member = tar.extractfile(entry)
                        if entry.name in ["Dockerfile", "dockerfile"]:
                            dockerfile = member.read()
                        else:
                            add_files[entry.name] = member.read()

            if not dockerfile:
                raise MissingError("The Dockerfile was missing...")

        fi = cls.create(user=user,
                        dockerfile=dockerfile,
                        additional_files=add_files,
                        created=arrow.utcnow().timestamp,
                        name=name,
                        status=False,
                        public=public,
                        rev=found+1,
                        disable=False)

        u = um.User(user)
        u.dockerfiles.append(fi.id)
        u.save()

        fi.queue_build()

        return fi


    def queue_build(self):
        self.status = False
        self.save()
        c.redis.rpush("build:queue", self.id)

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
            max_rev = r.table(self.table).filter({"name": self.name}).map(lambda user: user["rev"]).reduce(lambda left, right: r.branch(left>right,left,right)).run()

            img = r.table(self.table).filter({"name": self.name, "rev": max_rev}).pluck("id").coerce_to("array").run()
            if img and img[0]["id"] != self.id:
                self._latest = Dockerfile(img[0]["id"])

        return self._latest

    @property
    def latest_image(self, no_cache=False):
        if not self._latest_img or no_cache:
            max_rev = r.table(im.Image.table).filter({"dockerfile": self.id}).map(lambda user: user["rev"]).reduce(lambda left, right: r.branch(left>right,left,right)).run()

            img = r.table(im.Image.table).filter({"dockerfile": self.id, "rev": max_rev}).pluck("id").coerce_to("array").run()
            if img:
                self._latest_img = im.Image(img[0]["id"])

        return self._latest_img

    @property
    def ports(self, no_cache=False):
        if not self._ports or no_cache:
            string = cStringIO.StringIO(self.dockerfile)

            p= []

            for line in string:
                line = line.strip(" \n")
                if line.startswith("EXPOSE"):
                    ps = line[6:].strip(" ").split(" ")
                    p.extend(ps)

            self._ports = p

        return self._ports

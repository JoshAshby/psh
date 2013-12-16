"""

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import tarfile
import arrow
import cStringIO

from errors.general import \
      NotFoundError, MissingError

import rethinkdb as r
from rethinkORM import RethinkModel
from models.rethink.user import userModel as um

import config.config as c


class Image(RethinkModel):
    table = "images"

    def finish_init(self):
        if not self._data:
            raise NotFoundError("Dockerfile was not found.")

        self._formated_created = ""
        self._ports = []
        self._latest = None
        self._user = None

    @classmethod
    def new_image(cls, user_id, name, file_obj, public=False, override=False):
        found = r.table(cls.table).filter({'name': name, 'user_id': user_id}).count().run()

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

        fi = cls.create(user_id=user_id,
                        dockerfile=dockerfile,
                        additional_files=add_files,
                        created=arrow.utcnow().timestamp,
                        name=name,
                        public=public,
                        rev=found+1,
                        build_status="queue",
                        disable=False)

        fi.queue_build()

        return fi

    def add_image(self, build_status, log, docker_id=None):
        self.log = log
        self.build_status = build_status
        self.docker_id = docker_id

        self.save()

    def queue_build(self):
        self.save()
        c.redis.rpush("build:queue", self.id)

    @property
    def formated_created(self, no_cache=False):
        if not self._formated_created or no_cache:
            self._formated_created = arrow.get(self.created).format(c.general.time_format)

        return self._formated_created

    @property
    def latest(self, no_cache=False):
        if not self._latest or no_cache:
            max_rev = r.table(self.table).filter({"name": self.name}).map(lambda user: user["rev"]).reduce(lambda left, right: r.branch(left>right,left,right)).run()

            img = r.table(self.table).filter({"name": self.name, "rev": max_rev}).pluck("id").coerce_to("array").run()
            if img and img[0]["id"] != self.id:
                self._latest = Image(img[0]["id"])

        return self._latest

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

    @property
    def user(self, no_cache=False):
        if not self._user or no_cache:
            self._user = um.User(self.user_id)

        return self._user

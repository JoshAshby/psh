#!/usr/bin/env python
"""
bucket model

Basically what we have is a key value store in redis
of all the session ID's (store and retrieved via the cookie
from Seshat)

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import config.config as c
import models.utils.dbUtils as dbu
from config.standard import StandardConfig


class CfgBuckets(StandardConfig):
    def __init__(self, redis=c.general.redis):
        self._redis = redis
        keys = {}
        for key in self._redis.keys("bucket:*:status"):
            val = dbu.toBoolean(self._redis.get(key))

            name_key = ':'.join([key.rsplit(":", 1)[0], "name"])
            name= c.general.redis.get(name_key)

            desc_key = ':'.join([key.rsplit(":", 1)[0], "description"])
            desc = c.general.redis.get(desc_key)

            ID = key.split(":")[1]
            keys[ID] = StandardConfig(name=name, description=desc, status=val, id=ID)

        self._data = keys

    def __iter__(self):
        for bit in self._data:
            yield self._data[bit]

    def __len__(self):
        return len(self._data)

    @property
    def list(self):
        return [ self._data[item] for item in self._data ]

    def new(self, ID, name, description, status=False):
        """
        Creates a new bucket with the given name, status and description.

        :type description: String
        :type name: String
        :type status: Boolean
        """
        self._redis.set("bucket:{}:status".format(ID), status)
        self._redis.set("bucket:{}:description".format(ID), description)
        self._redis.set("bucket:{}:name".format(ID), name)

        return name

    def delete(self, ID):
        for item in ["status", "description", "name"]:
            key = "bucket:{key}:{item}".format(key=ID, item=item)
            self._redis.delete(key)

        return True

    def edit(self, ID, name=None, description=None, status=None):
        if status:
            self._redis.set("bucket:{}:status".format(ID), status)
        if description:
            self._redis.set("bucket:{}:description".format(ID), description)
        if name:
            self._redis.set("bucket:{}:name".format(ID), name)

        return True

    def toggle(self, ID):
        """
        Toggles the given bucket via `ID` to the inverse of its current value
        """
        key = "bucket:{}:status".format(ID)
        current = dbu.toBoolean(self._redis.get(key))
        return self._redis.set(key, not current)

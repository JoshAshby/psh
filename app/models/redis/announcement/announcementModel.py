#!/usr/bin/env python
"""
Announcement model

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import uuid
import config.config as c
import models.utils.dbUtils as dbu
from utils.standard import StandardODM

import arrow


def all_announcements():
    keys = []
    for key in c.redis.keys("announcement:*:status"):
        data = {}
        val = dbu.toBoolean(c.redis.get(key))
        ID = key.split(":")[1]
        ann_key = ':'.join([key.rsplit(":", 1)[0], "message"])
        message = c.redis.get(ann_key)

        ann_time_created_key = ':'.join([key.rsplit(":", 1)[0], "created"])
        time_created = arrow.get(c.redis.get(ann_time_created_key))

        data = {"message": message,
                "status": val,
                "id": ID,
                "created": time_created.timestamp,
                "formated_created": time_created.format("MM/DD/YYYY HH:mm")}


        ann_start_key = ':'.join([key.rsplit(":", 1)[0], "start"])
        start = c.redis.get(ann_start_key)
        if start and start != '0':
            start = arrow.get(start)
            data["start"] = start.timestamp
            data["formated_start"] = start.format("MM/DD/YYYY HH:mm")
        else:
            data["start"] = 0

        ann_end_key = ':'.join([key.rsplit(":", 1)[0], "end"])
        end = c.redis.get(ann_end_key)
        if end and end != '0':
            end = arrow.get(end)
            data["end"] = end.timestamp
            data["formated_end"] = end.format("MM/DD/YYYY HH:mm")
        else:
            data["end"] = 0

        keys.append(data)

    return keys


class CfgAnnouncements(StandardODM):
    def __init__(self, redis=c.redis):
        self._redis = redis
        keys = {}
        for key in self._redis.keys("announcement:*:status"):
            val = dbu.toBoolean(self._redis.get(key))

            ann_start_key = ':'.join([key.rsplit(":", 1)[0], "start"])
            start = c.redis.get(ann_start_key)

            ann_end_key = ':'.join([key.rsplit(":", 1)[0], "end"])
            end = c.redis.get(ann_end_key)

            start = long(start) if start else 0
            end = long(end) if end else 0

            now = arrow.utcnow().timestamp
            if (start and end) and not (start <= now and now < end):
                val = False
            elif start and start > now:
                val = False
            elif end and end < now:
                val = False

            if val:
                ID = key.split(":")[1]
                ann_key = ':'.join([key.rsplit(":", 1)[0], "message"])
                message = self._redis.get(ann_key)

                keys[ID] = message

        self._data = keys

    def __iter__(self):
        for bit in self._data:
            yield self._data[bit]

    def new_announcement(self, message, status, start=0, end=0):
        """
        Creates a new announcement, with a UUID for the key ID, consisting of
        the current status and message

        :type message: String
        :type status: Boolean
        """
        ID = uuid.uuid4()
        self._redis.set("announcement:%s:status" % ID, status)
        self._redis.set("announcement:%s:message" % ID, message)
        self._redis.set("announcement:%s:created" % ID, arrow.utcnow().timestamp)

        self._redis.set("announcement:%s:start" % ID, start)
        self._redis.set("announcement:%s:end" % ID, end)

        return ID

    def edit_announcement(self, ID, message, status, start=0, end=0):
        """
        Allows for an announcement to be changed
        """
        self._redis.set("announcement:%s:status" % ID, status)
        self._redis.set("announcement:%s:message" % ID, message)

        self._redis.set("announcement:%s:start" % ID, start)
        self._redis.set("announcement:%s:end" % ID, end)

        return True

    def toggle_announcement(self, ID):
        """
        Toggles the given announcement via `ID` to the inverse of its current value
        """
        current = dbu.toBoolean(self._redis.get("announcement:%s:status"%ID))
        return self._redis.set("announcement:%s:status"%ID, not current)

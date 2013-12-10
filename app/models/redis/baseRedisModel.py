#!/usr/bin/env python
"""
Seshat interface for the redis model.

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import config.config as c
from models.redis.redisModel import RedisModel


class SeshatRedisModel(RedisModel):
    def __init__(self, key, redis=c.general.redis, **kwargs):
        super(SeshatRedisModel, self).__init__(key, redis, **kwargs)

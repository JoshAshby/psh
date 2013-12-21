#!/usr/bin/env python
"""
For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import config.config as c
import logging

logger = logging.getLogger(c.general.appName+".hipache")


def route_container_ports(con):
    for domain in con.domains:
        name = ":".join([con.user.username, con.name, domain])
        port = con.ports[con.http_port]

        logger.debug("Adding route for {}->localhost:{}"\
             .format(domain, port))

        key = "frontend:{}".format(domain)
        val = "http://127.0.0.1:{}".format(port)

        c.redis.rpush(key, name, val)

def remove_container_routes(con, new_domains):
    domains_to_remove = set(con.domains).difference(set(new_domains))

    for domain in domains_to_remove:
        logger.debug("Removing route for {}"\
             .format(domain))
        c.redis.delete("frontend:{}".format(domain))

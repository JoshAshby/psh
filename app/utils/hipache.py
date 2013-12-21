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
    port = con.ports[con.http_port]

    for domain in con.domains:
        name = ":".join([con.user.username, con.name, domain])
        update_route(domain, "http://127.0.0.1", port, name)

def remove_container_routes(con, new_domains):
    domains_to_remove = set(con.domains).difference(set(new_domains))

    for domain in domains_to_remove:
        remove_route(domain)

def add_or_extend_route(url_from, url_to, port, name):
    key = "frontend:{}".format(url_from)
    val = "{}:{}".format(url_to, port)

    if not c.redis.exists(key):
        c.redis.rpush(key, name, val)
    else:
        c.redis.rpush(key, val)

    logger.debug("Adding route for {}->{}:{}"\
         .format(url_from, url_to, port))

def remove_route(domain):
    logger.debug("Removing route for {}"\
         .format(domain))

    c.redis.delete("frontend:{}".format(domain))

def update_route(domain_from, domain_to, port, name):
    remove_route(domain_from)
    add_or_extend_route(domain_from, domain_to, port, name)

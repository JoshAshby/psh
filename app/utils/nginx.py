#!/usr/bin/env python
"""
For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2012
http://joshashby.com
joshuaashby@joshashby.com
"""
from views.template import template
import utils.files as fu
import config.config as c

import cStringIO


def container_nginx_config(container):
    tmpl = template.PartialTemplate("config/nginx")
    tmpl.data = {"hostname": container.hostname}

    filz = cStringIO.cStringIO()

    for port, options in container.ports.iteritems():
        if options["route"]:
          tmpl.data = {"internal_port": options["internal"],
                       "host_port": options["host"]}

          filz.write(tmpl.render())

    filz.seek(0)
    path = "/".join([c.dirs.nginx, container.hostname])
    fu.write_file(path, filz)

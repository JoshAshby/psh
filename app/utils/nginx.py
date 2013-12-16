#!/usr/bin/env python
"""
For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2012
http://joshashby.com
joshuaashby@joshashby.com
"""
from views import template as t
import utils.files as fu
import config.config as c

import cStringIO


def container_nginx_config(container):
    tmpl = t.PartialTemplate("configs/nginx")
    tmpl.data = {"container": container}

    filz = cStringIO.StringIO()
    filz.write(tmpl.render())

    filz.seek(0)
    name = "_".join([container.user.id, container.name])
    path = "/".join([c.dirs.nginx, name])
    fu.write_file(path, filz)

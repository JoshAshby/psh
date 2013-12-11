#!/usr/bin/env python
"""
TEMPLATE ALL THE THINGS WITH Jinja (And Mustache)!!!!
Uses the Jinja templating language to make a base template object by which is
easy to work with in the controllers, and a walker and templateFile objects
which provide automatic reading and rereading in debug mode of template files.

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import pystache
import os
import config.config as c
import logging
import yaml
import jinja2
import arrow

logger = logging.getLogger(c.general["logName"]+".views")

time_format = "dd MMM DD HH:mm:ss:SS YYYY"
config_delim = "+++"
default_theme_color = "red"


tmplPath = os.path.dirname(__file__)+"/raw_templates/"

tmpls = {}


class templateFile(object):
    def __init__(self, fileBit):
        """
        Reads in fileBit into memory, and sets the modified time for the
        object to that of the file at the current moment.
        """
        self._file_bit = fileBit
        self._file = ''.join([tmplPath, fileBit])
        self._mtime = 0

        self._config = {}
        self._read_template()

    @property
    def template(self):
        """
        Returns the template, while reading it in if the file has been
        modified since we first read it in, and only if we are in debug
        mode. Otherwise this will just return the template stored in memory
        from first read/startup.
        """
        if c.general["debug"]:
            self._read_template()

        return self._template

    @property
    def config(self):
        return self._config

    @property
    def extension(self):
        return self._file.rsplit(".", 1)[1]

    @property
    def is_jinja(self):
        return self.extension=="jinja"

    @property
    def is_mustache(self):
        return self.extension=="mustache"

    def _read_template(self):
        """
        Read in the template only if it has been modified since we first
        read it into our `_template`
        """
        mtime = os.path.getmtime(self._file)

        if self._mtime < mtime:
            if c.general["debug"]:
                pt = arrow.get(self._mtime).format(time_format)
                nt = arrow.get(mtime).format(time_format)
                logger.debug("""\n\r============== Template =================
    Rereading template into memory...
    TEMPLATE:  %s
    TYPE: %s
    OLD MTIME: %s
    NEW MTIME: %s
""" % (self._file, self.extension, pt, nt))

            with open(self._file, "r") as openTmpl:
                raw = unicode(openTmpl.read())

            self._mtime = mtime

            self._raw = raw
            template = self._parse_raw()

            if(self.is_mustache):
                self._template = template
            if(self.is_jinja):
                self._template = jinja2.Template(template)

    def _parse_raw(self):
        if self._raw[:3] == config_delim:
            config, template = self._raw.split("+++", 2)[1:]
            self._config = yaml.load(config)
        else:
            template = self._raw

        return template

    def render(self, data):
        _data = self._config.copy()
        _data.update(data)

        if(self.is_jinja):
            return unicode(self.template.render(_data))
        else:
            result = pystache.render(self.template, _data)
            return unicode(result)

    def __contains__(self, item):
        return item in self._config

    def __getitem__(self, item):
        return self._config[item]

    def __setitem__(self, item, value):
        self._config[item] = value


class template(object):
    def __init__(self, template, data=None):
        if data is None: data = {}
        self._baseData = {
            "req": data,
            "stylesheets": [],
            "scripts": "",
            "scriptFiles": []
        }

        self._template = template
        self._base = "skeleton_navbar"

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value):
        assert type(value) is str
        self._template = value

    @property
    def skeleton(self):
        return self._base

    @skeleton.setter
    def skeleton(self, value):
        assert type(value) == str
        self._base = value

    @skeleton.deleter
    def skeleton(self):
        self._base = ""

    @property
    def data(self):
        return self._baseData

    @data.setter
    def data(self, value):
        assert type(value) == dict
        self._baseData.update(value)

    def append(self, value):
        self.data = value

    def update(self, value):
        self.data = value

    @property
    def scripts(self):
        return self._baseData["scriptFiles"], self._baseData["scripts"]

    @scripts.setter
    def scripts(self, value):
        if type(value) == list:
            self._baseData["scriptFiles"].extend(value)
        else:
          self._baseData["scripts"] += value

    @property
    def stylesheets(self):
        return self._baseData["stylesheets"], self._baseData["styles"]

    @stylesheets.setter
    def stylesheets(self, value):
        if type(value) == list:
            self._baseData["stylesheets"].extend(value)
        else:
            self._baseData["styles"] += value

    @stylesheets.deleter
    def stylesheets(self):
        self._baseData["stylesheets"] = []

    def partial(self, placeholder, template, data=None):
        if data is None: data = {}
        assert type(data) is dict
        data.update(self._baseData.copy())
        self._baseData[placeholder] = tmpls[template].render(data)

    def render(self):
        data = self._baseData.copy()

        template = tmpls[self._template]
        body = template.render(data)

        data.update(template.config.copy())

        if "base" in template:
            base = template["base"]
        else:
            base = self._base

        if not "theme_color" in template and not "theme_color" in data:
            data["theme_color"] = default_theme_color

        if base is not None and base:
            baseTmpl= tmpls[base]
            data["body"] = body

            _render = baseTmpl.render(data)

        else:
            _render = body

        self._baseData = {}
        data = {}

        del data
        del self._baseData

        return unicode(_render)


class PartialTemplate(template):
    def render(self):
        data = self._baseData.copy()

        template = tmpls[self._template]
        body = template.render(data)

        body = body if body else ""

        del data

        return unicode(body)


for top, folders, files in os.walk(tmplPath):
    for fi in files:
        base = top.split(tmplPath)[1]
        file_name, extension = fi.rsplit('.', 1)
        if extension in ["mustache", "jinja"]:
            name = '/'.join([base, file_name]).lstrip('/')
            fi = '/'.join([base, fi])
            tmpls[name] = templateFile(fi)

#!/usr/bin/env python
"""
Seshat
Web App/API framework built on top of gevent
route table

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""


class RouteTable(object):
    def __init__(self):
        self._data = {}

    def append(self, url):
        self._data[url.url] = url

    def get(self, parsed_url):
        """
        Attempts to find the closest match to the given url.
        Its messy but it gets the job done. mostly well. not sure on
        the amount of processing time it has or hasn't saved however,
        but it doesn't use regex... :/

        :parsed_url: urlparse.ParseResult
        """
        obj = None
        extended = ""
        base = None
        orig_path = parsed_url.path.rstrip("/")
        if not orig_path:
            base = "/"
        else:
            if orig_path in self._data:
                base = orig_path
            else:
                found = False
                path = orig_path
                while not found:
                    path_parts = path.rsplit("/", 1)
                    base = path_parts[0]
                    if base in self._data:
                        found = True
                        extended = orig_path[len(base)+1:]
                    else:
                        path = path_parts[0]
                        if not path:
                            base = None
                            found = True
        if base is not None:
            obj = self._data[base].pageObject
        print extended
        return obj, extended

    def __repr__(self):
        routes = ""
        routes_template = "\t{key}:\n\t\t{value}\n"
        for route in self._data:
            route = routes_template.format(key=route, value=self._data[route])
            routes = ''.join([routes, route])

        string = "< RouteTable @ {id} Table:\n{table}\n >"
        string = string.format(**{
            "id": id(self),
            "table": routes
          })
        return string

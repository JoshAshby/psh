#!/usr/bin/env python
"""
Pagination object for use in templates

For more information, see: https://github.com/JoshAshby/

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import rethinkdb as r
from rethinkORM import RethinkCollection
from operator import itemgetter

import urllib
import math

from config.standard import StandardConfig
from views.template import PartialTemplate


class Paginate(StandardConfig):
    def __init__(self, pail, request, sort="", perpage_default=24, sort_direction=""):
        """
        Now: PAGINATE ALL THE THINGS.

        General pagination object that can handle a plain list, a list of dicts or
        other objects that behave similarly, or a rethink rql query or collection

        Once initialized with a list or query, and a requestItem object, it will use
        "perpage" "page" and "dir" in the request params (or defaults) to compute
        the needed information and finish the query, setting the objects `pail`
        property to the result. It will also sort, if given a sort parameter.

        After initialized, the resulting, paginated and sorted results should be
        grabed from the `pail` attribute.

        :param pail: Either a List, or a Rethink RQL query
        :param request: The requestItem
        :param sort: The field within dictionaries, or RQL to sort by, only useful
        if the List is a List of Dicts or Similar objects.
        :para perpage_default: The default for how many objects to display per page
        """
        self._data = {
            "perpage_default": perpage_default,
            "offset": 6,
            "perpage": request.getParam("perpage", perpage_default),
            "page": request.getParam("page", 0, int),
            "sort_direction": request.getParam("dir", "desc") if not sort_direction else sort_direction,
            "sort": sort
        }

        self._pail = pail

        self._request = request

        self._calc()

    def _calc(self):
        """
        Internal function for calculating the pagination options and such
        that are passed to the templates.
        """
        page_dict = {}

        if type(self._pail) is list:
            if self.sort:
                self._pail.sort(key=itemgetter(self.sort), reverse=True)
            else:
                self._pail.sort()

            if self.sort_direction == "asc":
                self._pail.reverse()

        elif isinstance(self._pail, RethinkCollection):
            if self.sort and self.sort_direction == "asc":
                self._pail.order_by(self.sort, "desc")
            elif self.sort:
                self._pail.order_by(self.sort, "asc")

            self._pail.fetch()

        else:
            di = self.sort
            if self.sort_direction == "desc":
                di = r.asc(self.sort) # Yeah, yeah, I know...
            if self.sort_direction == "asc":
                di = r.desc(self.sort) # Yeah, yeah, I know again... Don't ask

            self._pail = self._pail.order_by(di)

        if self.perpage != "all":
            page_dict["show"] = True

            perpage = int(self.perpage)
            page = int(self.page)

            offset_start = (perpage * page)
            offset_end = offset_start + perpage

            if type(self._pail) is list:
                length = len(self._pail)
            elif isinstance(self._pail, RethinkCollection):
                length = self._pail._query.count().run()
            else:
                length = self._pail.count().run()

            if length <= perpage:
                page_dict["show"] = False

            if page != 0:
                page_dict["has_prev"] = True
            else:
                page_dict["has_prev"] = False

            if length > offset_end:
                page_dict["has_next"] = True
            else:
                page_dict["has_next"] = False

            if type(self._pail) is list:
                self._pail = self._pail[offset_start:offset_end]
            elif isinstance(self._pail, RethinkCollection):
                self._pail.limit(perpage, offset_start)
            else:
                self._pail = self._pail.skip(offset_start).limit(perpage)

            pages = math.ceil(length/perpage)+1

            page_dict["last_page"] = int(pages)-1
            page_dict["count_start"] = int(max([min([page-math.ceil(self.offset/2)+1, pages-self.offset]), 0]))
            page_dict["count_end"] = int(min([max([page+math.floor(self.offset/2)+1, self.offset]), pages]))

        else:
            page_dict["show"] = False

        if type(self._pail) is not list and not isinstance(self._pail, RethinkCollection):
            results = list(self._pail.run())
            self._pail = results
        elif isinstance(self._pail, RethinkCollection):
            self._pail.fetch()

        self._page_dict = page_dict

    @property
    def pail(self):
        """
        Return the sorted and paginated results
        """
        return self._pail

    @property
    def _query_string(self, extra=None):
        """
        Internal function for generating a query string so that perpage and
        other parameters that are acting as options aren't lost on each
        page increment/decrement.
        """
        if extra is None: extra = {}
        extra_pre = self._request.params.copy()
        extra_pre.pop("page", None)
        extra.update(extra_pre)
        return urllib.urlencode(extra)

    @property
    def options(self):
        """
        Generate and return a string consisting of two selects
        and an update/submit button to be used for the pagination options form.
        """
        tmpl = PartialTemplate("partials/options", self._request)
        tmpl.data.update(self._page_dict)
        tmpl.data.update(self._data)
        tmpl.data.update({"query": self._query_string})

        return tmpl.render()

    @property
    def pager(self):
        """
        Generate and return a string consisting of just a simple pager:
        next and previous buttons.
        """
        tmpl = PartialTemplate("partials/pager", self._request)
        tmpl.data.update(self._page_dict)
        tmpl.data.update(self._data)
        tmpl.data.update({"query": self._query_string})

        return tmpl.render()

    @property
    def paginate(self):
        """
        Generate and return a string consisting of a full pagination module.
        Next, previous, first, last and page numbers.
        """
        tmpl = PartialTemplate("partials/paginate", self._request)
        tmpl.data.update(self._page_dict)
        tmpl.data.update(self._data)
        tmpl.data.update({"query": self._query_string})

        return tmpl.render()

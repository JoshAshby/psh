#!/usr/bin/env python
"""
session model

Takes advantage of collections to make a dynamic system allowing
both regular needed session data along with temporary session data storage
available to the system through the requests object

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import bcrypt
import models.redis.baseRedisModel as brm
import errors.session as use
import json

import models.rethink.user.userModel as um
import rethinkdb as r


class session(brm.SeshatRedisModel):
    _protected_items = []
    def _finish_init(self):
        if not hasattr(self, "raw_alerts"): self.raw_alerts = "[]"
        if not hasattr(self, "username"): self.username = ""
        if not hasattr(self, "id"): self.id = ""
        if not hasattr(self, "groups"): self.groups = []
        self._HTML_alerts = ""

    def _get(self, item):
        if "groups" in self._keys:
            if "has_" in item:
                if "root" in self.groups or item[4:] in self.groups:
                    return True
                else:
                    return False
        return super(session, self)._get(item)

    def login_without_check(self, user):
        """
        Tries to find the user in the database, if the user is successfully
        logged in then the sessions username and user ID is set to that users

        :param user: Str of the username or ID to try and login
        :type user: Str

        :returns: True if the user was successfully logged in
        """
        foundUser = list(r.table(um.User.table).filter({'username': user}).run())
        if len(foundUser) > 0:
            foundUser = um.User(foundUser[0]["id"])
            if not foundUser.disable:
                self.username = foundUser.username
                self.id = foundUser.id
                self.groups = foundUser.groups
                return True
            else:
                raise use.DisableError("Your user is currently disabled. \
                        Please contact an admin for additional information.")
        raise use.UsernameError("We can't find your user, are you \
                sure you have the correct information?")

    def login(self, user, password):
        """
        Tries to find the user in the database,then tries to use the plain text
        password from `password` to match against the known password hash in
        the users object. If the user is successfully logged in then the sessions
        username and user ID is set to that users

        :param user: Str of the username or ID to try and login
        :type user: Str
        :param password: Clear text str of the users password to hash and check
        :type password: Str

        :returns: True if the user was successfully logged in
        """
        foundUser = list(r.table(um.User.table).filter({'username': user}).run())
        if len(foundUser) > 0:
            foundUser = um.User(**foundUser[0])
            if not foundUser.disable:
                if foundUser.password == bcrypt.hashpw(password,
                        foundUser.password):
                    self.username = foundUser.username
                    self.id = foundUser.id
                    self.groups = foundUser.groups
                    return True
                else:
                    raise use.PasswordError("Your password appears to \
                            be wrong.")
            else:
                raise use.DisableError("Your user is currently disabled. \
                        Please contact an admin for additional information.")
        raise use.UsernameError("We can't find your user, are you \
                sure you have the correct information?")

    def logout(self):
        """
        Sets the users loggedIn to False then removes the link between their
        session and their `userORM`
        """
        self.username = ""
        self.id = ""
        self.groups.reset()
        return True

    def push_alert(self, message, quip="", level="success"):
        """
        Creates an alert message to be displayed or relayed to the user,
        This is a higher level one for use in HTML templates.
        All params are of type str

        :param message: The text to be placed into the main body of the alert
        :param quip: Similar to a title, however just a quick attention getter
        :param level: Can be any of `success` `error` `info` `warning`
        """
        alerts = json.loads(self.raw_alerts)
        alerts.append({"msg": message, "level": level, "expire": "next", "quip": quip})
        self.raw_alerts = json.dumps(alerts)

    @property
    def alerts(self, no_cache=False):
        """
        Returns a list of dictonary elements representing the users alerts

        :return: List of Dicts
        """
        if not self._HTML_alerts or no_cache:
            self._render_alerts() # cache results if we haven't already,
                                  #   or if we're overriding the cache
        return self._HTML_alerts

    @alerts.deleter
    def alerts(self):
        """
        Clears the current users expired alerts.
        """
        alerts = json.loads(self.raw_alerts)
        for alert in alerts:
            if alert["expire"] == "next":
                alerts.pop(alerts.index(alert))

        self.raw_alerts = json.dumps(alerts)

    def _render_alerts(self):
        alerts = json.loads(self.raw_alerts)

        alertStr = ""
        for alert in alerts:
            if alert["level"] == "info":
                alert["icon"] = "info"
            elif alert["level"] == "success":
                alert["icon"] = "thumbs-up"
            elif alert["level"] == "warning":
                alert["icon"] = "excalmation"
            elif alert["level"] == "error":
                alert["icon"] = "warning"
                alert["level"] = "danger"

            alertStr += ("""<div class="alert alert-{level}"><i class="fa fa-{icon}"></i><strong>{quip}</strong> {msg}</div>""").format(**alert)

        self._HTML_alerts = unicode(alertStr)

    def has_perm(self, group_name):
        if group_name in self.groups or "root" in self.groups:
            return True
        return False

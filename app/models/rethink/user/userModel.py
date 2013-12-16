"""
User model for use in seshat built off of rethinkdb

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
import arrow
import bcrypt

from errors.user import \
      PasswordError, UsernameError, EmailError
from errors.general import \
      NotFoundError

import rethinkdb as r
from rethinkORM import RethinkModel

import hashlib

import config.config as c


class User(RethinkModel):
    table = "users"
    _protected_items = ["formated_about", "formated_created"]

    def finish_init(self):
        if not self._data:
            raise NotFoundError("User was not found.")

        self._formated_created = ""
        self._gravatar = ""

    @classmethod
    def new_user(cls, username, password, email):
        """
        Make a new user, checking for username conflicts. If no conflicts are
        found the password is encrypted with bcrypt and the resulting `userORM` returned.

        :param username: The username that should be used for the new user
        :param password: The plain text password that should be used for the password.
        :return: `userORM` if the username is available,
        """
        if password == "":
            raise PasswordError("Password cannot be null")

        found_u = r.table(cls.table).filter({'username': username}).count().run()
        found_e = r.table(cls.table).filter({'email': email}).count().run()
        if not found_u and not found_e:
            passwd = bcrypt.hashpw(password, bcrypt.gensalt())
            user = cls.create(username=username,
                              password=passwd,
                              created=arrow.utcnow().timestamp,
                              disable=False,
                              email=email,
                              groups=[])

            return user

        elif found_u:
            raise UsernameError("That username is taken, please choose again.",
                                username)

        elif found_e:
            raise EmailError("That email is already in our system.", email)

    def set_password(self, password):
        """
        Sets the users password to `password`

        :param password: plain text password to hash
        """
        self.password = bcrypt.hashpw(password, bcrypt.gensalt())
        self.save()

    @property
    def formated_created(self, no_cache=False):
        if not self._formated_created or no_cache:
            self._formated_created = arrow.get(self.created).format(c.general.time_format)

        return self._formated_created

    @property
    def gravatar(self, no_cache=False):
        """
        Generates a Gravatar email hash
        """
        if not self._gravatar or no_cache:
            self._gravatar = hashlib.md5(self.email.strip(" ").lower()).hexdigest()

        return self._gravatar

    def has_perm(self, group_name):
        if group_name in self.groups:
            return True

        return False

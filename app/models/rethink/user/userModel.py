"""
User model for use in seshat built off of rethinkdb

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""
from rethinkORM import RethinkModel
import arrow
import bcrypt

from errors.user import \
      PasswordError, UsernameError
from errors.general import \
      NotFoundError

import rethinkdb as r


class User(RethinkModel):
    table = "users"
    _protected_items = ["formated_about", "formated_created"]

    def finish_init(self):
        if not self._data:
            raise NotFoundError("User was not found.")

    @classmethod
    def new_user(cls, username, password):
        """
        Make a new user, checking for username conflicts. If no conflicts are
        found the password is encrypted with bcrypt and the resulting `userORM` returned.

        :param username: The username that should be used for the new user
        :param password: The plain text password that should be used for the password.
        :return: `userORM` if the username is available,
        """
        if password == "":
            raise PasswordError("Password cannot be null")

        found = r.table(cls.table).filter({'username': username}).count().run()
        if not found:
            passwd = bcrypt.hashpw(password, bcrypt.gensalt())
            user = cls.create(username=username,
                       password=passwd,
                       created=arrow.utcnow().timestamp,
                       disable=False,
                       groups=[])
            return user
        else:
            raise UsernameError("That username is taken, please choose again.",
                    username)

    def set_password(self, password):
        """
        Sets the users password to `password`

        :param password: plain text password to hash
        """
        self.password = bcrypt.hashpw(password, bcrypt.gensalt())
        self.save()

    def format(self):
        """
        Formats markdown and dates into the right stuff
        """
        self.formated_created = arrow.get(self.created)

    def has_perm(self, group_name):
        if group_name in self.groups:
            return True
        return False

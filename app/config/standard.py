#!/usr/bin/env python
"""
Base config object to take a dict and make it function more object like

Also helpful for converting a dict into a standard object style interface.

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com
"""


class StandardConfig(object):
    _data = {}
    def __init__(self, *args, **kwargs):
        """
        Override this to make a custom object from a key:value set of data

        So long as this sets its internal _data dict
        """
        if len(args) > 1:
            raise Exception("Can't pass multiple arguments")

        if len(args) == 1 and type(args[0]) is dict:
            self._data = args[0]

        self._data = kwargs

    def _get(self, item):
        """
        Helper function to keep the __getattr__ and __getitem__ calls
        KISSish
        """
        if item[0] != "_":
            data = object.__getattribute__(self, "_data")
            if item in data:
                return data[item]
        return object.__getattribute__(self, item)

    def _set(self, item, value):
        """
        Helper function to keep the __setattr__ and __setitem__ calls
        KISSish

        Will only set the objects _data if the given items name is not prefixed
        with _ or if the item exists in the protected items List.
        """
        if item[0] != "_":
            keys = object.__getattribute__(self, "_data")
            if not hasattr(value, '__call__'):
                keys[item] = value
                return value
            if hasattr(value, '__call__') and item in keys:
                raise Exception("""Cannot set model data to a function, same \
name exists in data""")
        return object.__setattr__(self, item, value)

    def __getattr__(self, item):
        return self._get(item)

    def __getitem__(self, item):
        return self._get(item)

    def __setattr__(self, item, value):
        return self._set(item, value)

    def __setitem__(self, item, value):
        return self._set(item, value)

    def __delitem__(self, item):
        """
        Deletes the given item from the objects _data dict, or if from the
        objects namespace, if it does not exist in _data.
        """
        keys = object.__getattribute__(self, "_data")
        if item in keys:
            del(keys[item])
        else:
            object.__delitem__(self, item)

    def __contains__(self, item):
        """
        Allows for the use of syntax similar to::

            if "blah" in model:

        This only works with the internal _data, and does not include other
        properties in the objects namepsace.
        """
        keys = object.__getattribute__(self, "_data")
        if item in keys:
            return True
        return False

    def __repr__(self):
        """
        Returns the objects internal data object, which is a dict

        :return: The internal data
        :rtype: Dict
        """
        return self._data

    def __str__(self):
        return str(self._data)

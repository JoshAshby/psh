#!/usr/bin/env python
"""
helper utils for mainly the redis db models

http://xkcd.com/353/

Josh Ashby
2013
http://joshashby.com
joshuaashby@joshashby.com

"""
import rethinkdb as r


def toBoolean(str):
    if str == 'True':
        return True

    elif str == 'False':
        return False

    else:
        raise Exception("Not a boolean")


def rql_where_not(table, field, value):
    """
    Generates a query that is equivlent to running:

    The SQL ~equ to what I'm aiming for
        SELECT * FROM model WHERE id NOT IN ( SELECT * FROM model WHERE field == value )

    This query can then be passed off to collections or used for anything else.
    This may or may not get fairly slow once you start getting a lot of id's...
    """
    hidden_ids = r.table(table).filter(r.row[field].eq(value)).concat_map(lambda doc: [doc["id"]]).coerce_to("array").run()

    query = r.table(table).filter(lambda doc: ~r.expr(hidden_ids).contains(doc["id"]))
    return query


def rql_highest_revs(query, field):
    """
    r.db("psh").table("images").groupedMapReduce(
      function(image) {
        return image('dockerfile')
      },
      function(image) {
        return {rev: image('rev'), id: image('id')}
      },
      function(left, right) {
        return r.branch(left('rev').gt(right('rev')), left, right)
      }
    ).map(
      function(group) {
        return group('reduction')("id")
      }
    )
    """
    ids = query.grouped_map_reduce(
        lambda image: image[field],
        lambda image: {"rev": image["rev"], "id": image["id"]},
        lambda left, right: r.branch(left["rev"]>right["rev"], left, right)
    ).map(lambda group: group["reduction"]["id"]).coerce_to("array").run()

    return query.filter(lambda doc: r.expr(ids).contains(doc["id"]))

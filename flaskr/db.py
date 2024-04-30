import sqlite3
import datetime

import click
from flask import current_app, g


def convert_timestamp(val):
    """Convert Unix epoch timestamp to datetime.datetime object."""
    return datetime.datetime.strptime(val.decode("utf-8"), "%Y-%m-%d %H:%M:%S")


sqlite3.register_converter("timestamp", convert_timestamp)


def get_db():
    """returns the db connection."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """If db is not None, the connection is closed."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """gets db connection and executes schema.sql unto it."""
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """registers init_db_command to the app, tells Flask to close the db connection when the app is closed."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

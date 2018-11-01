"""Experiment access module."""

import mysql.connector as conn


def connect(user, password, host, database):
    """Use credentials to connect to a MySQL Database."""
    cnx = conn.connect(
        user=user,
        password=password,
        host=host,
        database=database
        )
    return cnx


def build_table():
    pass

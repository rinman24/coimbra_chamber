"""Experiment access module."""

import mysql.connector


def connect(user, password, host, database):
    """Use credentials to connect to a MySQL Database."""
    cnx = mysql.connector.connect(
        user=user,
        password=password,
        host=host,
        database=database
        )
    return cnx

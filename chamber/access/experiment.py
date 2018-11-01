"""Experiment access module."""

import mysql.connector as conn


def connect(schema):
    cnx = conn.connect(schema)
    return cnx

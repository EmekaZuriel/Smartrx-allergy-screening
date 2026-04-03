

import psycopg2
import psycopg2.extras
import os

def _get_connection_string() -> str:
    """Read the DB connection string from st.secrets (Streamlit Cloud)
    or fall back to the NEON_DB_CONNECTION_STRING environment variable."""
    try:
        import streamlit as st
        return st.secrets["NEON_DB_CONNECTION_STRING"]
    except Exception:
        pass
    conn_str = os.getenv("NEON_DB_CONNECTION_STRING")
    if not conn_str:
        raise ValueError(
            "Database connection string not found. "
            "Set NEON_DB_CONNECTION_STRING in Streamlit secrets or as an environment variable."
        )
    return conn_str
    
class Database:
    CONNECTION = None

    @staticmethod
    def _connect():
        Database.CONNECTION = psycopg2.connect(_get_connection_string())

    @staticmethod
    def ensure_connection():
        # Reconnect if the connection is new or has been closed/dropped by the server
        if Database.CONNECTION is None or Database.CONNECTION.closed != 0:
            Database._connect()
        cursor = Database.CONNECTION.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return cursor

    @staticmethod
    def fetch_all(query, params=None):
        try:
            cursor = Database.ensure_connection()
            cursor.execute(query, params or ())
            return [dict(row) for row in cursor.fetchall()]
        except psycopg2.OperationalError:
            # Connection appeared alive but was actually dead — force reconnect and retry
            Database.CONNECTION = None
            cursor = Database.ensure_connection()
            cursor.execute(query, params or ())
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def fetch_one(query, params=None):
        try:
            cursor = Database.ensure_connection()
            cursor.execute(query, params or ())
            row = cursor.fetchone()
            return dict(row) if row else None
        except psycopg2.OperationalError:
            Database.CONNECTION = None
            cursor = Database.ensure_connection()
            cursor.execute(query, params or ())
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def execute(query, params=None):
        try:
            cursor = Database.ensure_connection()
            cursor.execute(query, params or ())
            Database.CONNECTION.commit()
        except psycopg2.OperationalError:
            Database.CONNECTION = None
            cursor = Database.ensure_connection()
            cursor.execute(query, params or ())
            Database.CONNECTION.commit()

    @staticmethod
    def close():
        if Database.CONNECTION:
            Database.CONNECTION.close()
        Database.CONNECTION = None

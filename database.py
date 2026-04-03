

import psycopg2
import psycopg2.extras
import os

class Database:
    CONNECTION = None

    @staticmethod
    def _connect():
        conn_str = os.getenv(
            'NEON_DB_CONNECTION_STRING',
            "postgresql://neondb_owner:npg_mOYw2eQxMHs7@ep-shiny-scene-aby9kf9l-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        )
        Database.CONNECTION = psycopg2.connect(conn_str)

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
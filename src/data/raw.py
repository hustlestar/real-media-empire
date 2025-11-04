import logging
import psycopg2

from config import CONFIG

logger = logging.getLogger(__name__)


def get_connection(database=None):
    return psycopg2.connect(
        host=CONFIG.get("JDBC_HOST"),
        port=CONFIG.get("JDBC_PORT"),
        database=database if database else CONFIG.get("JDBC_DATABASE"),
        user=CONFIG.get("JDBC_USER_NAME"),
        password=CONFIG.get("JDBC_PASSWORD"),
    )

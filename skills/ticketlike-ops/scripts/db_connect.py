#!/usr/bin/env python3
"""
Conexión rápida a TiDB Cloud — ticketlike.mx producción.
Uso: import db_connect; conn = db_connect.get_connection()
O ejecutar directamente: python3 db_connect.py "SELECT COUNT(*) FROM events;"
"""

import ssl
import sys

import pymysql

DB_CONFIG = {
    "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
    "port": 4000,
    "user": "37Hy7adB53QmFW4.root",
    "password": "4N6caSwp0V4rxXp75HNO",
    "database": "R5HMD5sAyPAWW34dhuZc9u",
    "ssl": {"ca": None},
    "ssl_verify_identity": False,
    "ssl_verify_cert": False,
    "cursorclass": pymysql.cursors.DictCursor,
}


def get_connection():
    """Retorna una conexión pymysql lista para usar."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    config = {**DB_CONFIG, "ssl": ctx}
    return pymysql.connect(**config)


def query(sql, params=None):
    """Ejecuta una query y retorna los resultados como lista de dicts."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def execute(sql, params=None):
    """Ejecuta un statement (INSERT/UPDATE/DELETE) y hace commit."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            affected = cur.execute(sql, params)
            conn.commit()
            return affected
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sql = " ".join(sys.argv[1:])
        rows = query(sql)
        for row in rows:
            print(row)
    else:
        # Test de conexión
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as n FROM events")
            result = cur.fetchone()
            print(f"Conexión OK. Eventos en DB: {result['n']}")
        conn.close()

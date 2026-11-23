"""Histórico em SQLite para não repetir ofertas."""
import sqlite3
import time
from pathlib import Path

from . import config


def _con() -> sqlite3.Connection:
    Path(config.BANCO).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(config.BANCO)
    con.execute("""CREATE TABLE IF NOT EXISTS postados (
        id TEXT, grupo TEXT, quando INTEGER, nome TEXT, preco REAL, link TEXT)""")
    return con


def ja_postado(oferta_id: str) -> bool:
    limite = time.time() - config.NAO_REPETIR_DIAS * 86400
    with _con() as con:
        return con.execute("SELECT 1 FROM postados WHERE id=? AND quando>? LIMIT 1",
                           (oferta_id, limite)).fetchone() is not None


def registrar(oferta: dict, grupo: str) -> None:
    with _con() as con:
        con.execute("INSERT INTO postados VALUES (?,?,?,?,?,?)",
                    (oferta["id"], grupo, int(time.time()), oferta["nome"],
                     oferta["preco"], oferta["link"]))

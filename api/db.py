import sqlite3
from contextlib import closing
from pathlib import Path

# Always store the DB next to this file, no matter where uvicorn is started from
DB_PATH = Path(__file__).parent / "game.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT NOT NULL,
            score INTEGER NOT NULL
        )""")
    return conn


def add_score(player: str, score: int) -> None:
    with closing(get_connection()) as conn:
        with conn:  # commits on success
            conn.execute(
                "INSERT INTO scores (player, score) VALUES (?, ?)",
                (player, score),
            )


def get_top_scores(limit: int = 10) -> list[dict]:
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT player, score FROM scores "
            "ORDER BY score DESC, id ASC LIMIT ?",
            (limit,),
        ).fetchall()
    return [{"player": player, "score": score} for player, score in rows]
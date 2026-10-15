from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, StringConstraints

import db

app = FastAPI()

STATIC_DIR = Path(__file__).parent / "website"


class ScoreIn(BaseModel):
    player: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)
    ]
    score: int = Field(ge=0, le=100_000)


@app.get("/hello")
def hello():
    return {"message": "Sveiki!"}


@app.post("/scores", status_code=201)
def post_score(entry: ScoreIn):
    db.add_score(entry.player, entry.score)
    return {"status": "saved"}


@app.get("/scores")
def get_scores(limit: int = Query(10, ge=1, le=100)):
    return db.get_top_scores(limit)


# Must be last: serves leaderboard.html, rules.html, styles.css from /website
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
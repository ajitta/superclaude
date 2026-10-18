"""acme-web: the marketing site."""

import json
from pathlib import Path

from flask import Flask, render_template

STATIC = Path(__file__).resolve().parent / "static"
app = Flask(__name__)


@app.template_global()
def asset(name: str) -> str:
    manifest = json.loads((STATIC / "assets.json").read_text(encoding="utf-8"))
    return "/static/" + manifest.get(name, name)


@app.get("/")
def index():
    return render_template("index.html")

# main.py  — Zenplify “Master Tree” API (Render)

from pathlib import Path
from flask import Flask, request, jsonify
from notion_client import Client
import os, json

# ── Config ─────────────────────────────────────────────────────────
NOTION_TOKEN  = os.environ["NOTION_TOKEN"]          # set in Render
DB_CACHE_DIR  = Path("/tmp/db_ids")                 # persists per instance
DB_CACHE_DIR.mkdir(exist_ok=True)
DB_FILE       = DB_CACHE_DIR / "database_id.txt"
DB_NAME       = "Master Tree"

notion = Client(auth=NOTION_TOKEN)
app    = Flask(__name__)

# ── Helpers ────────────────────────────────────────────────────────
def create_master_tree() -> str:
    """Create the Master Tree DB on the first top-level page & return its ID."""
    top = notion.search(filter={"property": "object", "value": "page"})["results"][0]
    props = {
        "Name":   {"title": {}},
        "Notes":  {"rich_text": {}},
        "Tree":   {"select": {}},
        "Type":   {"select": {}},
        "Status": {"select": {}},
    }
    db = notion.databases.create(
        parent={"page_id": top["id"]},
        title=[{"type": "text", "text": {"content": DB_NAME}}],
        properties=props,
    )
    return db["id"]

def get_database_id() -> str:
    """Retrieve cached DB ID or create/cache a new one."""
    if DB_FILE.exists():
        return DB_FILE.read_text().strip()

    db_id = create_master_tree()
    DB_FILE.write_text(db_id)
    return db_id

DB_ID = get_database_id()   # resolves at startup

# ── Routes ─────────────────────────────────────────────────────────
@app.route("/add", methods=["POST"])
def add_item():
    data      = request.get_json(force=True)
    name      = data.get("Name")   or "Untitled"
    tree      = data.get("Tree")   or "Other"
    item_type = data.get("Type")
    status    = data.get("Status")
    notes     = data.get("Notes")

    props = {
        "Name":  {"title": [{"text": {"content": name}}]},
        "Tree":  {"select": {"name": tree}},
    }
    if item_type:
        props["Type"]   = {"select": {"name": item_type}}
    if status:
        props["Status"] = {"select": {"name": status}}
    if notes:
        props["Notes"]  = {"rich_text": [{"text": {"content": notes}}]}

    notion.pages.create(parent={"database_id": DB_ID}, properties=props)
    return jsonify({"message": "Item added"}), 200

# ── Health (optional) ──────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return "OK", 200

# ── Main ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

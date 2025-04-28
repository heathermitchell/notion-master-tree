# main.py  – Zenplify Master Tree API
from flask import Flask, request, jsonify
from notion_client import Client
import os
import json
from pathlib import Path

# ────────────────────────────────────────────
# 1)  CONFIG
# ────────────────────────────────────────────
NOTION_TOKEN = os.environ["NOTION_TOKEN"]          # already set in Render
DB_FILE       = Path("database_id.txt")            # stores the Master Tree ID
DB_NAME       = "Master Tree"

notion = Client(auth=NOTION_TOKEN)
app    = Flask(__name__)

# ────────────────────────────────────────────
# 2)  GET (or CREATE) DATABASE ID
# ────────────────────────────────────────────
def get_database_id() -> str:
    # a) stored locally?
    if DB_FILE.exists():
        return DB_FILE.read_text().strip()

    # b) otherwise create a new DB under the first top-level page
    parent_page = notion.search(filter={"property": "object", "value": "page"})["results"][0]["id"]

    # basic property skeleton (expand later if desired)
    props = {
        "Tree":   {"select": {"options": []}},
        "Type":   {"select": {"options": []}},
        "Status": {"select": {"options": []}},
        "Notes":  {"rich_text": {}},
    }

    db = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page},
        title= [{"type": "text", "text": {"content": DB_NAME}}],
        properties=props
    )

    DB_FILE.write_text(db["id"])      # persist for future runs
    return db["id"]


DATABASE_ID = get_database_id()

# ────────────────────────────────────────────
# 3)  OPENAPI SCHEMA  (GET "/")
# ────────────────────────────────────────────
@app.route("/", methods=["GET"])
def openapi_schema():
    return jsonify({
        "openapi": "3.1.0",
        "info": {"title": "Zenplify Master Tree API", "version": "1.1.0"},
        "paths": {
            "/add": {
                "post": {
                    "summary": "Add an item to the Master Tree",
                    "operationId": "addItem",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "Tree":   {"type": "string"},
                                        "Type":   {"type": "string"},
                                        "Status": {"type": "string"},
                                        "Notes":  {"type": "string"}
                                    },
                                    "required": ["Tree", "Type", "Status"]
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": "Item added"}}
                }
            }
        },
        "servers": [{"url": "https://notion-master-tree.onrender.com"}]
    })

# ────────────────────────────────────────────
# 4)  ADD ITEM ENDPOINT  (POST "/add")
# ────────────────────────────────────────────
@app.route("/add", methods=["POST"])
def add_item():
    data = request.get_json(force=True)

    notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            "Tree":   {"select": {"name": data["Tree"]}},
            "Type":   {"select": {"name": data["Type"]}},
            "Status": {"select": {"name": data["Status"]}},
            "Notes":  {"rich_text": [{"text": {"content": data.get("Notes","")}}]}
        }
    )
    return jsonify({"message": "Item added"}), 200


# ────────────────────────────────────────────
# 5)  START (Render uses the start command)
# ────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

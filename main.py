# main.py  – Zenplify Master Tree API
# ---------- CONFIG & HELPER ----------
DB_CACHE_DIR = Path("/tmp/db_ids")      # Render’s /tmp persists per instance
DB_CACHE_DIR.mkdir(exist_ok=True)

VALID_TREES = {"Brand", "Content", "SaaS", "AI Roles", "Other"}  # add more if needed

def _cache_path(tree: str) -> Path:
    return DB_CACHE_DIR / f"{tree.lower().replace(' ', '_')}_id.txt"

def get_or_create_db(tree_name: str) -> str:
    """Return the DB id for a given tree, creating & caching if missing."""
    cache_file = _cache_path(tree_name)
    if cache_file.exists():
        return cache_file.read_text().strip()

    # -- create fresh DB under first page in workspace --
    search = notion.search(filter={"property": "object", "value": "page"})
    if not search["results"]:
        raise RuntimeError("No parent page found to attach new database!")
    parent_id = search["results"][0]["id"]

    db = notion.databases.create(
        parent={"page_id": parent_id},
        title=[{"type": "text", "text": {"content": f"{tree_name} Tree"}}],
        properties=DATABASE_PROPERTIES   # keep using your existing dict
    )
    db_id = db["id"]
    cache_file.write_text(db_id)
    return db_id
# ---------- /CONFIG & HELPER ----------


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

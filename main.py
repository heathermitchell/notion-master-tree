print("🔥 Using the updated script!")

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/add", methods=["POST"])

def serve_openapi():
    schema = {
        "openapi": "3.0.0",
        "info": {
            "title": "Zenplify Master Tree API",
            "version": "1.0.0"
        },
        "servers": [
            {"url": "https://notion-master-tree.onrender.com/"}
        ],
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
                                        "Tree": {"type": "string"},
                                        "Type": {"type": "string"},
                                        "Status": {"type": "string"},
                                        "Notes": {"type": "string"}
                                    },
                                    "required": ["Tree", "Type"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Item added successfully"
                        }
                    }
                }
            }
        }
    }
    return jsonify(schema)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

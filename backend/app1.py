from flask import Flask, request, jsonify
from embeddings import get_embeddings, ingest_faq_csv
import pandas as pd
import os

app = Flask(__name__)

@app.route("/ingest_csv", methods=["POST"])
def ingest_csv():
    data = request.get_json()
    if not data or "file_path" not in data:
        return jsonify({"error": "Please provide 'file_path' in JSON"}), 400

    file_path = data["file_path"]

    if not os.path.exists(file_path):
        return jsonify({"error": f"File '{file_path}' does not exist"}), 400

    try:
        # Optional: preview CSV
        df = pd.read_csv(file_path)
        print("CSV preview:\n", df.head())

        # Load embeddings and ingest
        embeddings = get_embeddings()
        ingest_faq_csv(file_path, embeddings)

        return jsonify({"status": "success", "rows": len(df)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)

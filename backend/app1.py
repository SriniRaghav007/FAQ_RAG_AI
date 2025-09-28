from flask import Flask, request, jsonify
from embeddings import get_embeddings, ingest_faq_csv
from qa_chain import create_qa_chain
import os
import pandas as pd

app = Flask(__name__)

# Cache QA chain so it loads only once
qa_chain = None

def get_qa_chain():
    global qa_chain
    if qa_chain is None:
        qa_chain = create_qa_chain()  # heavy model, lazy-load
    return qa_chain

# --- CSV ingestion ---
@app.route("/ingest_csv", methods=["POST"])
def ingest_csv():
    data = request.get_json()
    if not data or "file_path" not in data:
        return jsonify({"error": "Please provide 'file_path' in JSON"}), 400

    file_path = data["file_path"]

    if not os.path.exists(file_path):
        return jsonify({"error": f"File '{file_path}' does not exist"}), 400

    try:
        df = pd.read_csv(file_path)
        embeddings = get_embeddings()
        ingest_faq_csv(file_path, embeddings)
        return jsonify({"status": "success", "rows": len(df)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- QA endpoint ---
@app.route("/ask_question", methods=["POST"])
def ask_question():
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Please provide 'question' in JSON"}), 400

    user_query = data["question"]

    try:
        chain = get_qa_chain()
        vectorstore = chain.retriever.vectorstore

        # Retrieve top 3 FAQs
        docs = vectorstore.similarity_search(user_query, k=3)
        top_faqs = [{"question": d.metadata["question"], "answer": d.metadata["answer"]} for d in docs]

        # Get model answer
        answer = chain.invoke({"query": user_query})["result"]

        return jsonify({
            "top_faqs": top_faqs,
            "model_answer": answer
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)

from flask import Flask, request, jsonify
from embeddings import get_embeddings, ingest_faq_csv
from qa_chain import create_qa_chain
import pandas as pd
import os
from datetime import datetime
from langchain_chroma import Chroma

app = Flask(__name__)

# --- Global QA chain and vectorstore ---
qa_chain = None

def get_qa_chain():
    global qa_chain
    if qa_chain is None:
        qa_chain = create_qa_chain()
    return qa_chain

# --- Ingest CSV (file upload) ---
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

# --- Ask a question ---
@app.route("/ask_question", methods=["POST"])
def ask_question():
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"status": "error", "error": "Provide 'question' in JSON"}), 400

    top_k = data.get("top_k", 3)
    question = data["question"]

    try:
        chain = get_qa_chain()
        vectorstore = chain.retriever.vectorstore

        # Retrieve top K FAQs
        docs = vectorstore.similarity_search(question, k=top_k)
        top_faqs = []
        for i, d in enumerate(docs, 1):
            top_faqs.append({
                "faq_id": getattr(d.metadata, "id", i),
                "question": d.metadata["question"],
                "answer": d.metadata["answer"],
            })

        # Model answer
        model_answer = chain.invoke({"query": question})["result"]

        return jsonify({
            "status": "success",
            "top_faqs": top_faqs,
            "model_answer": model_answer,
            "model_version": "flan-t5-large",
            "query_timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# --- List all ingested FAQs ---
@app.route("/list_faqs", methods=["GET"])
def list_faqs():
    try:
        chain = get_qa_chain()
        vectorstore = chain.retriever.vectorstore

        # Retrieve all docs
        docs = vectorstore.similarity_search("", k=1000)  # arbitrary large number
        faqs = [{"question": d.metadata["question"], "answer": d.metadata["answer"]} for d in docs]

        return jsonify({"status": "success", "faqs": faqs})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# --- Delete all FAQs / reset vectorstore ---
@app.route("/delete_faqs", methods=["POST"])
def delete_faqs():
    try:
        global qa_chain
        chain = get_qa_chain()
        vectorstore = chain.retriever.vectorstore

        # Delete the collection if it exists
        try:
            vectorstore._collection.delete()  # Chroma internal delete
            print("Chroma collection cleared.")
        except Exception:
            # Collection might not exist yet
            print("Chroma collection does not exist, creating a new one.")


        # Remove the Chroma persist directory to fully clear all data
        chroma_dir = os.getenv("CHROMA_DB_DIR", "./chroma_store")
        import shutil
        try:
            if os.path.exists(chroma_dir):
                shutil.rmtree(chroma_dir)
                print(f"Chroma persist directory '{chroma_dir}' deleted.")
        except Exception as e:
            print(f"Failed to delete Chroma persist directory: {e}")

        # Reset the global qa_chain so it is rebuilt on next use
        qa_chain = None

        return jsonify({"status": "success", "message": "All FAQs deleted, vectorstore and persist directory reset"})

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    try:
        _ = get_qa_chain()
        return jsonify({"status": "success", "message": "QA chain loaded"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# --- Run server ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)

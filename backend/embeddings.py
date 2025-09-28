# embeddings_ingestion.py
import os
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_store")

# ---- Embeddings (shared) ----
def get_embeddings():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    return HuggingFaceEmbeddings(model_name=model_name)

def question_exists(vectorstore, question_text):
    # Search for the exact question in the collection
    results = vectorstore.similarity_search(question_text, k=1)
    if results:
        top = results[0]
        # If the top result is very similar / same text, consider it a duplicate
        return top.metadata["question"].strip().lower() == question_text.strip().lower()
    return False

# ---- Ingest CSV into Chroma ----
def ingest_faq_csv(csv_path, embeddings):
    df = pd.read_csv(csv_path)
    if not {"Question", "Answer"}.issubset(df.columns):
        raise ValueError("CSV must have Question and Answer columns")
    
    vectorstore = Chroma(
        collection_name="faqs",
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR
    )

    # Optional: deduplicate within CSV
    df = df.drop_duplicates(subset=["Question", "Answer"])

    added_count = 0
    for _, row in df.iterrows():
        question, answer = row["Question"], row["Answer"]
        if not question_exists(vectorstore, question):
            vectorstore.add_texts(
                texts=[f"{question} {answer}"],
                metadatas=[{"question": question, "answer": answer}]
            )
            added_count += 1

    print(f"Ingested {added_count} new FAQs into ChromaDB (duplicates skipped).")

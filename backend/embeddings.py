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

    # Optional: deduplicate before ingestion
    df = df.drop_duplicates(subset=["Question", "Answer"])

    texts = (df["Question"] + " " + df["Answer"]).tolist()
    metadatas = [{"question": q, "answer": a} for q, a in zip(df["Question"], df["Answer"])]

    vectorstore.add_texts(texts=texts, metadatas=metadatas)
    print(f"Ingested {len(texts)} FAQs into ChromaDB.")

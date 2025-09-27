import os
import pandas as pd
from dotenv import load_dotenv

# LangChain imports
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# Hugging Face Transformers
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# ---- Load environment variables ----
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_store")

# ---- Step 1: Read CSV ----
def read_faq_csv(csv_path: str):
    df = pd.read_csv(csv_path)
    if not {"Question", "Answer"}.issubset(df.columns):
        raise ValueError("CSV must have columns: Question and Answer")
    return df

# ---- Step 2: Initialize embeddings ----
def init_embeddings():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    return HuggingFaceEmbeddings(model_name=model_name)

# ---- Step 3: Initialize Chroma Vector Store ----
def init_chromadb(embeddings):
    vectorstore = Chroma(
        collection_name="faqs",
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR
    )
    return vectorstore

# ---- Step 4: Ingest data into Chroma ----
def ingest_faqs_to_chroma(vectorstore, df):
    texts = (df["Question"] + " " + df["Answer"]).tolist()
    metadatas = [{"question": q, "answer": a} for q, a in zip(df["Question"], df["Answer"])]
    vectorstore.add_texts(texts=texts, metadatas=metadatas)
    print(f"Ingested {len(texts)} FAQs into ChromaDB.")

# ---- Step 5: Initialize Hugging Face LLM ----
def init_hf_llm(model_name="google/flan-t5-small"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    pipe = pipeline(
        task="text2text-generation",
        model=model,
        tokenizer=tokenizer,
        device=-1,  # CPU, change to 0 for GPU
        max_length=256
    )
    return HuggingFacePipeline(pipeline=pipe)
def show_retrieved_docs(vectorstore, query, k=3):
    docs = vectorstore.similarity_search(query, k=k)
    print("\n=== Retrieved Similar FAQs ===")
    for i, d in enumerate(docs, start=1):
        print(f"{i}. Question: {d.metadata['question']}")
        print(f"   Answer: {d.metadata['answer']}\n")
    return docs


def create_qa_chain(vectorstore, llm):
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are a helpful assistant. Use the following context to answer the question.


Context:
{context}

Question:
{question}

Answer in full, precise sentences, including explanations of commands if applicable.
"""
    )
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt}
    )

def ask_question(qa_chain, question):
    # Simply pass the question as "query"
    return qa_chain.invoke({"query": question})["result"]


# ---- Script Entrypoint ----
if __name__ == "__main__":
    csv_path = "faqs.csv"
    df = read_faq_csv(csv_path)

    embeddings = init_embeddings()
    vectorstore = init_chromadb(embeddings)
    ingest_faqs_to_chroma(vectorstore, df)

    llm = init_hf_llm()
    qa_chain = create_qa_chain(vectorstore, llm)

    # Interactive test
    while True:
        query = input("\nAsk a question (type 'exit' to quit): ")
        if query.lower() == "exit":
            break
        show_retrieved_docs(vectorstore, query, k=3)
        answer = ask_question(qa_chain, query)
        print(f"\nAnswer: {answer}")

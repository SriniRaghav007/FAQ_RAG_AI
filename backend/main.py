# main.py
from embeddings import get_embeddings, ingest_faq_csv
from qa_chain import create_qa_chain

def run_ingestion(csv_path):
    embeddings = get_embeddings()
    ingest_faq_csv(csv_path, embeddings)

def run_qa_interactive():
    qa_chain = create_qa_chain()
    vectorstore = qa_chain.retriever.vectorstore

    while True:
        query = input("\nAsk a question (type 'exit' to quit): ")
        if query.lower() == "exit":
            break

        # Show retrieved FAQs
        docs = vectorstore.similarity_search(query, k=3)
        print("\n=== Retrieved FAQs ===")
        for i, d in enumerate(docs, 1):
            print(f"{i}. Q: {d.metadata['question']}")
            print(f"   A: {d.metadata['answer']}")

        # Ask the model
        answer = qa_chain.invoke({"query": query})["result"]
        print(f"\nAnswer: {answer}")

if __name__ == "__main__":
    choice = input("Type 'ingest' to upload CSV or 'qa' to ask questions: ").strip().lower()
    if choice == "ingest":
        csv_file = input("Enter CSV file path: ").strip()
        run_ingestion(csv_file)
    elif choice == "qa":
        run_qa_interactive()
    else:
        print("Invalid choice.")

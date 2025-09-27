# qa_chain_setup.py
from langchain_huggingface import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from embeddings import get_embeddings
import os

CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_store")

# ---- Load vectorstore ----
def get_vectorstore():
    embeddings = get_embeddings()
    return Chroma(
        collection_name="faqs",
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR
    )

# ---- Initialize Hugging Face LLM ----
def init_llm(model_name="google/flan-t5-small"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    pipe = pipeline(
        task="text2text-generation",
        model=model,
        tokenizer=tokenizer,
        device=-1,
        max_length=256
    )
    return HuggingFacePipeline(pipeline=pipe)

# ---- Default Prompt Template ----
DEFAULT_PROMPT = """
You are a helpful assistant. Use the following context to answer the question.

Context:
{context}

Question:
{question}

Answer in full, precise sentences.
"""

# ---- Create or modify chain ----
def create_qa_chain(llm=None, prompt_template=DEFAULT_PROMPT):
    vectorstore = get_vectorstore()
    prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)
    if llm is None:
        llm = init_llm()
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt}
    )
    return qa_chain

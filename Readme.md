# FAQ AI – RAG Pipeline

## Q/A for testing 
| Question                                                                     | Answer                                                                                                                                 |
| ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| How do I initialize a new Git repository in my local machine?                | Use `git init` in your project directory. This creates a new `.git` folder and starts tracking your files with Git.                    |
| What’s the difference between `git pull` and `git fetch`?                    | `git fetch` downloads commits from the remote but doesn’t merge them. `git pull` fetches **and merges** them into your current branch. |
| How can I recover a file I accidentally deleted in Git?                      | If it was staged or committed, use `git checkout -- <file>` to restore it from the last commit.                                        |
| What is a Git branch and why is it used?                                     | A branch is a pointer to a commit that allows you to work on features or fixes in isolation from the main codebase.                    |
| How do I resolve merge conflicts when combining two branches?                | Open conflicting files, edit to reconcile differences, then stage (`git add`) and commit the resolved files.                           |
| Can I contribute to an open-source project without write access to the repo? | Yes — fork the repository, make changes in your fork, and submit a pull request to the original repo.                                  |
| How do I generate and add an SSH key to my GitHub account?                   | Use `ssh-keygen` to generate a key, then copy it to GitHub via Settings → SSH and GPG keys → New SSH key.                              |
| What’s the difference between GitHub Issues and Pull Requests?               | Issues track bugs, tasks, or feature requests; Pull Requests propose code changes for review and merging.                              |
| How can I roll back to a previous commit without losing history?             | Use `git revert <commit-hash>` to create a new commit that undoes changes without rewriting history.                                   |
| What are some best practices for writing good commit messages?               | Keep the summary under 50 characters, explain **what** and **why** in the body, and write in imperative mood (e.g., “Fix bug…”).       |

I used the above Q/A for testing the RAG pipeline which ingested 151 faq from the file faqs.csv. and answers using the text-to-text generation model google/flan-t5-large, with device=-1 which runs on cpu

# STEPS to run the code
- Add the chromaStore location to env
- create venv and install the requirements from requirements.txt
- python3 -m venv venv_name
- source venv_name/bin/activate
- pip3 install -r requirements1.txt
- python3 main.py
- `ingest` to run

#  About the project

This project demonstrates a Retrieval-Augmented Generation (RAG) pipeline using local embeddings and a Hugging Face text-to-text model (google/flan-t5-large). It allows you to ingest FAQs from a CSV and answer user questions with context-aware responses.

Features

- Ingest FAQ CSV into a Chroma vector store.

- Perform similarity search over FAQs using embeddings.

- Generate answers with Hugging Face text-to-text models.

- Interactive Q&A via CLI (future plans: Streamlit/Flask UI).

- Dynamic prompt templates and adjustable model parameters.

## Setup instructions

- git clone <repo_url>
- cd <repo_folder>
- Create a .env file in the project root with:
- CHROMA_DB_DIR=./chroma_store
- Create and activate a virtual environment: python3 -m venv venv_name
source venv_name/bin/activate
- pip3 install -r requirements.txt
- Prepare the FAQ CSV:
Ensure the CSV file has columns Question and Answer.
Example: faqs.csv with 151 FAQs for testing.
- You can also use the faqGenerator, to replace the list with your own list and get a csv file with Question and Answer Columns
- If you want to run the code as a script
- Run the main script: python3 main.py
You will be prompted with a choice:
Type ingest to load the CSV and generate embeddings (first-time setup).
Type qa to ask questions interactively.
After choosing qa, input questions.

The system will display the top retrieved FAQs along with the generated answer.
- Type exit to quit.

- The current setup uses google/flan-t5-large on CPU (device=-1), which may be slower for large models.

- Only the vectorstore needs to be *ingested once*, the ingestion doesnt not check for duplicates which will lead to problems in retrieval ( ingesting same thing more than once); subsequent runs can directly query the store.

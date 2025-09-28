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

Q/A for testing

# STEPS to run the code
- Add it to env
- create venv and install the requirements from requirements.txt

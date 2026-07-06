from github import Github
from config import GITHUB_TOKEN

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found in .env")

# Create GitHub client
from github import Github, Auth

auth = Auth.Token(GITHUB_TOKEN)
github = Github(auth=auth)


def get_repo(repo_name):
    """
    Returns the GitHub repository object.
    Example:
        repo_name = "AtinDimri/Test_repo"
    """
    return github.get_repo(repo_name)


def get_commit(repo_name, commit_sha):
    """
    Returns a commit object.
    """
    repo = get_repo(repo_name)
    return repo.get_commit(commit_sha)


def get_parent_sha(commit):
    """
    Returns the parent commit SHA.
    Returns None if this is the initial commit.
    """
    if commit.parents:
        return commit.parents[0].sha
    return None


def get_files(commit):
    """
    Returns a list of changed files.
    """
    return list(commit.files)


# --------------------------
# Temporary Testing Section
# --------------------------

if __name__ == "__main__":

    REPO_NAME = "AtinDimri/Test_repo"

    COMMIT_SHA = "23acb5ef9ce53219af0beeb79fbd31c76235d0f4"

    commit = get_commit(REPO_NAME, COMMIT_SHA)

    print("=" * 60)
    print("Repository      :", REPO_NAME)
    print("Commit SHA      :", commit.sha)
    print("Parent SHA      :", get_parent_sha(commit))
    print("Author          :", commit.commit.author.name)
    print("Commit Message  :", commit.commit.message)
    print("Commit Date     :", commit.commit.author.date)

    print("\nChanged Files")
    print("-" * 60)

    files = get_files(commit)

    for file in files:
        print(f"File      : {file.filename}")
        print(f"Status    : {file.status}")
        print(f"Additions : {file.additions}")
        print(f"Deletions : {file.deletions}")
        print(f"Changes   : {file.changes}")
        print("-" * 60)

    print("=" * 60)
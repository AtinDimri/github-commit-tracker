from github import Github, Auth
from config import GITHUB_TOKEN

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found. Check your .env file.")

# ------------------------------------
# GitHub Authentication
# ------------------------------------

auth = Auth.Token(GITHUB_TOKEN)
github = Github(auth=auth)


# ------------------------------------
# Repository Functions
# ------------------------------------

def get_repo(repo_name):
    """
    Example:
        repo_name = "AtinDimri/Test_repo"
    """
    return github.get_repo(repo_name)


def get_commit(repo_name, commit_sha):
    repo = get_repo(repo_name)
    return repo.get_commit(commit_sha)


def get_parent_sha(commit):
    if commit.parents:
        return commit.parents[0].sha
    return None


def get_files(commit):
    return list(commit.files)


# ------------------------------------
# File Content Functions
# ------------------------------------

def get_file_content(repo_name, file_path, ref):
    """
    Downloads the content of a file at a specific commit.

    Parameters
    ----------
    repo_name : str
    file_path : str
    ref : branch / tag / commit SHA

    Returns
    -------
    str
    """

    repo = get_repo(repo_name)

    try:
        file = repo.get_contents(file_path, ref=ref)

        if isinstance(file, list):
            raise Exception(f"{file_path} is a directory.")

        return file.decoded_content.decode("utf-8")

    except Exception as e:
        raise Exception(
            f"Unable to fetch '{file_path}' at ref '{ref}'.\n{e}"
        )


def get_old_and_new_file(repo_name, parent_sha, commit_sha, file_path):
    """
    Returns:

        old_content,
        new_content
    """

    old_content = get_file_content(
        repo_name,
        file_path,
        parent_sha
    )

    new_content = get_file_content(
        repo_name,
        file_path,
        commit_sha
    )

    return old_content, new_content


# ------------------------------------
# Temporary Testing
# ------------------------------------

if __name__ == "__main__":

    REPO_NAME = "AtinDimri/Test_repo"

    COMMIT_SHA = "23acb5ef9ce53219af0beeb79fbd31c76235d0f4"

    commit = get_commit(REPO_NAME, COMMIT_SHA)

    parent_sha = get_parent_sha(commit)

    print("=" * 70)
    print("Repository :", REPO_NAME)
    print("Commit SHA :", COMMIT_SHA)
    print("Parent SHA :", parent_sha)
    print("=" * 70)

    files = get_files(commit)

    for file in files:

        print("\nFile :", file.filename)

        old_text, new_text = get_old_and_new_file(
            REPO_NAME,
            parent_sha,
            COMMIT_SHA,
            file.filename
        )

        print("\nOLD FILE")
        print("-" * 40)
        print(old_text)

        print("\nNEW FILE")
        print("-" * 40)
        print(new_text)

        print("\n" + "=" * 70)

# --------------------------
# Temporary Testing Section
# --------------------------

# if __name__ == "__main__":

#     REPO_NAME = "AtinDimri/Test_repo"

#     COMMIT_SHA = "23acb5ef9ce53219af0beeb79fbd31c76235d0f4"

#     commit = get_commit(REPO_NAME, COMMIT_SHA)

#     print("=" * 60)
#     print("Repository      :", REPO_NAME)
#     print("Commit SHA      :", commit.sha)
#     print("Parent SHA      :", get_parent_sha(commit))
#     print("Author          :", commit.commit.author.name)
#     print("Commit Message  :", commit.commit.message)
#     print("Commit Date     :", commit.commit.author.date)

#     print("\nChanged Files")
#     print("-" * 60)

#     files = get_files(commit)

#     for file in files:
#         print("=" * 70)
#         print("File:", file.filename)
#         print("=" * 70)

#         print(file.patch)

#         print("=" * 70)
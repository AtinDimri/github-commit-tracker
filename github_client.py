from github import Github
from config import GITHUB_TOKEN

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN is missing in .env")

_github = Github(GITHUB_TOKEN)


def get_repo(full_name: str):
    return _github.get_repo(full_name)


def get_commit(full_name: str, sha: str):
    repo = get_repo(full_name)
    return repo.get_commit(sha)


def get_parent_sha(commit) -> str:
    if commit.parents and len(commit.parents) > 0:
        return commit.parents[0].sha
    return ""


def get_file_content(full_name: str, path: str, ref: str) -> str:
    repo = get_repo(full_name)
    content = repo.get_contents(path, ref=ref)
    return content.decoded_content.decode("utf-8", errors="replace")


#TO VERIFY---
if __name__ == "__main__":
    repo_name = "AtinDimri/Test_repo"
    commit_sha = "23acb5ef9ce53219af0beeb79fbd31c76235d0f4"

    commit = get_commit(repo_name, commit_sha)
    print("Commit SHA:", commit.sha)
    print("Message:", commit.commit.message)
    print("Parent SHA:", get_parent_sha(commit))
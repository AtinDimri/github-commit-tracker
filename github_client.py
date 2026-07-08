import os
from github import Github, Auth


def _get_token() -> str:
    token = (
        os.getenv("GITHUB_TOKEN")
        or os.getenv("GH_PAT")
        or os.getenv("INPUT_GH_PAT")
    )
    if not token:
        raise RuntimeError(
            "GitHub token not found. Expected GITHUB_TOKEN, GH_PAT, or INPUT_GH_PAT."
        )
    return token


def get_github_client() -> Github:
    auth = Auth.Token(_get_token())
    return Github(auth=auth)


def get_repo(repo_name: str):
    return get_github_client().get_repo(repo_name)


def get_commit(repo_name: str, commit_sha: str):
    repo = get_repo(repo_name)
    return repo.get_commit(commit_sha)


def get_parent_sha(commit):
    if commit.parents:
        return commit.parents[0].sha
    return None


def get_files(commit):
    return list(commit.files)


def get_file_content(repo_name: str, file_path: str, ref: str) -> str:
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


def get_old_and_new_file(
    repo_name: str,
    parent_sha: str,
    commit_sha: str,
    file_path: str,
):
    old_content = get_file_content(repo_name, file_path, parent_sha)
    new_content = get_file_content(repo_name, file_path, commit_sha)
    return old_content, new_content
import pytest
import os
import shutil
import subprocess
import tempfile

@pytest.fixture(scope="function")
def temp_dir():
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def remote_repo(temp_dir):
    # Setup a dummy remote repository
    repo_path = os.path.join(temp_dir, "remote-repo.git")
    os.makedirs(repo_path)

    # Initialize bare repo
    subprocess.check_call(["git", "init", "--bare"], cwd=repo_path)

    # Clone it to add some content
    clone_path = os.path.join(temp_dir, "temp-clone")
    subprocess.check_call(["git", "clone", repo_path, clone_path])

    # Configure user for commit
    subprocess.check_call(["git", "config", "user.email", "test@example.com"], cwd=clone_path)
    subprocess.check_call(["git", "config", "user.name", "Test User"], cwd=clone_path)

    # Add a file
    with open(os.path.join(clone_path, "README.md"), "w") as f:
        f.write("# Test Repo")

    # Add a config file to test copying
    with open(os.path.join(clone_path, ".env"), "w") as f:
        f.write("FOO=BAR")

    subprocess.check_call(["git", "add", "."], cwd=clone_path)
    subprocess.check_call(["git", "commit", "-m", "Initial commit"], cwd=clone_path)
    subprocess.check_call(["git", "push", "origin", "master"], cwd=clone_path)

    # Create another branch
    subprocess.check_call(["git", "checkout", "-b", "feature/test"], cwd=clone_path)
    with open(os.path.join(clone_path, "feature.txt"), "w") as f:
        f.write("Feature content")
    subprocess.check_call(["git", "add", "."], cwd=clone_path)
    subprocess.check_call(["git", "commit", "-m", "Feature commit"], cwd=clone_path)
    subprocess.check_call(["git", "push", "origin", "feature/test"], cwd=clone_path)

    # Return the path to the remote bare repo
    return repo_path

@pytest.fixture(scope="session")
def scripts_dir():
    # Return absolute path to the scripts directory (repo root)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

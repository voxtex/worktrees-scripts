import os
import subprocess
import pytest

@pytest.fixture
def setup_repo(temp_dir, remote_repo, scripts_dir):
    """Sets up a cloned repo using wtclone.sh to test wtadd on."""
    wtclone_script = os.path.join(scripts_dir, "wtclone.sh")
    project_name = "test-project"
    cmd = [wtclone_script, remote_repo, project_name]
    subprocess.check_call(cmd, cwd=temp_dir)
    return os.path.join(temp_dir, project_name)

def test_wtadd_new_branch(setup_repo, scripts_dir):
    """Test creating a new branch/worktree."""
    wtadd_script = os.path.join(scripts_dir, "wtadd.sh")
    repo_path = setup_repo

    new_branch = "new-feature"
    cmd = [wtadd_script, new_branch]

    # Run wtadd inside the repo directory
    subprocess.check_call(cmd, cwd=repo_path)

    # Verify worktree directory created
    # The script replaces slashes with underscores for directory names, but "new-feature" has none.
    worktree_path = os.path.join(repo_path, new_branch)
    assert os.path.exists(worktree_path)

    # Verify it's a git repo
    assert os.path.exists(os.path.join(worktree_path, ".git"))

    # Verify branch created
    # Check HEAD ref in the worktree
    head_ref = subprocess.check_output(["git", "symbolic-ref", "HEAD"], cwd=worktree_path).decode().strip()
    assert head_ref == f"refs/heads/{new_branch}"

    # Verify .env was copied (it existed in master)
    # The script copies .env, .envrc, etc. from current HEAD (which was master when we ran wtclone)
    assert os.path.exists(os.path.join(worktree_path, ".env"))
    with open(os.path.join(worktree_path, ".env"), "r") as f:
        assert f.read() == "FOO=BAR"

def test_wtadd_existing_remote_branch(setup_repo, scripts_dir):
    """Test adding a worktree for an existing remote branch."""
    wtadd_script = os.path.join(scripts_dir, "wtadd.sh")
    repo_path = setup_repo

    # "feature/test" exists in remote (created in conftest.py)
    branch_name = "feature/test"
    cmd = [wtadd_script, branch_name]

    subprocess.check_call(cmd, cwd=repo_path)

    # Script behavior: dirname=${branchname//\//_} -> feature_test
    expected_dir = "feature_test"
    worktree_path = os.path.join(repo_path, expected_dir)

    assert os.path.exists(worktree_path)

    # Verify content specific to that branch
    assert os.path.exists(os.path.join(worktree_path, "feature.txt"))

    # Verify branch is checked out
    head_ref = subprocess.check_output(["git", "symbolic-ref", "HEAD"], cwd=worktree_path).decode().strip()
    assert head_ref == f"refs/heads/{branch_name}"

def test_wtadd_single_argument_behavior(setup_repo, scripts_dir):
    """Test wtadd behavior with a single argument.

    Note: The script usage text suggests `wtadd WORKTREE_NAME [BRANCH_NAME]`, but the implementation
    only uses the first argument as the branch name (and derives the directory name from it).
    This test verifies the actual behavior.
    """
    wtadd_script = os.path.join(scripts_dir, "wtadd.sh")
    repo_path = setup_repo

    branch_name = "another-feature"
    cmd = [wtadd_script, branch_name]
    subprocess.check_call(cmd, cwd=repo_path)

    assert os.path.exists(os.path.join(repo_path, branch_name))

    head_ref = subprocess.check_output(["git", "symbolic-ref", "HEAD"], cwd=os.path.join(repo_path, branch_name)).decode().strip()
    assert head_ref == f"refs/heads/{branch_name}"

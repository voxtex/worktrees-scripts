import os
import subprocess
import pytest

@pytest.fixture
def setup_repo_for_remove(temp_dir, remote_repo, scripts_dir):
    """Sets up a repo with a worktree to remove."""
    wtclone_script = os.path.join(scripts_dir, "wtclone.sh")
    wtadd_script = os.path.join(scripts_dir, "wtadd.sh")
    project_name = "remove-project"

    # Clone
    subprocess.check_call([wtclone_script, remote_repo, project_name], cwd=temp_dir)
    repo_path = os.path.join(temp_dir, project_name)

    # Add a worktree
    subprocess.check_call([wtadd_script, "to-be-removed"], cwd=repo_path)

    return repo_path

def test_wtremove_basic(setup_repo_for_remove, scripts_dir):
    """Test removing a worktree."""
    wtremove_script = os.path.join(scripts_dir, "wtremove.sh")
    repo_path = setup_repo_for_remove
    worktree_name = "to-be-removed"

    worktree_path = os.path.join(repo_path, worktree_name)
    assert os.path.exists(worktree_path)

    # Run wtremove.sh
    subprocess.check_call([wtremove_script, worktree_name], cwd=repo_path)

    # Verify directory is gone
    assert not os.path.exists(worktree_path)

    # Verify branch is deleted
    # We can check available branches in the bare repo
    # Or try to resolve the ref
    # git show-ref refs/heads/to-be-removed should fail

    # Use git in the repo_path (which is the root containing .git -> .bare)
    # Note: running git commands in `repo_path` (which contains .git file) works.

    try:
        subprocess.check_call(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{worktree_name}"], cwd=repo_path)
        branch_exists = True
    except subprocess.CalledProcessError:
        branch_exists = False

    assert not branch_exists, "Branch should have been deleted"

def test_wtremove_multiple(setup_repo_for_remove, scripts_dir):
    """Test removing multiple worktrees."""
    wtadd_script = os.path.join(scripts_dir, "wtadd.sh")
    wtremove_script = os.path.join(scripts_dir, "wtremove.sh")
    repo_path = setup_repo_for_remove

    # Add two more
    subprocess.check_call([wtadd_script, "wt1"], cwd=repo_path)
    subprocess.check_call([wtadd_script, "wt2"], cwd=repo_path)

    assert os.path.exists(os.path.join(repo_path, "wt1"))
    assert os.path.exists(os.path.join(repo_path, "wt2"))

    # Remove both
    subprocess.check_call([wtremove_script, "wt1", "wt2"], cwd=repo_path)

    assert not os.path.exists(os.path.join(repo_path, "wt1"))
    assert not os.path.exists(os.path.join(repo_path, "wt2"))

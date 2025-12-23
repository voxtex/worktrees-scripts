import os
import subprocess
import pytest

@pytest.fixture
def setup_repo_with_worktrees(temp_dir, remote_repo, scripts_dir):
    """Sets up a repo with a couple of worktrees."""
    wtclone_script = os.path.join(scripts_dir, "wtclone.sh")
    wtadd_script = os.path.join(scripts_dir, "wtadd.sh")
    project_name = "list-project"

    # Clone
    subprocess.check_call([wtclone_script, remote_repo, project_name], cwd=temp_dir)
    repo_path = os.path.join(temp_dir, project_name)

    # Add a worktree
    subprocess.check_call([wtadd_script, "feature-a"], cwd=repo_path)

    return repo_path

def test_wtlist_output(setup_repo_with_worktrees, scripts_dir):
    """Test that wtlist.sh lists worktrees correctly."""
    wtlist_script = os.path.join(scripts_dir, "wtlist.sh")
    repo_path = setup_repo_with_worktrees

    # Run wtlist.sh
    output = subprocess.check_output([wtlist_script], cwd=repo_path).decode()

    # Verify output contains the repo name
    assert "list-project" in output or "remote-repo" in output # remote-repo is the origin name

    # Verify it lists 'master' (created by clone)
    assert "master" in output

    # Verify it lists 'feature-a'
    assert "feature-a" in output

    # Verify it formats as table (check for some structure)
    lines = output.strip().split('\n')
    # Filter for lines containing our worktrees
    master_lines = [l for l in lines if "master" in l]
    feature_lines = [l for l in lines if "feature-a" in l]

    assert len(master_lines) > 0
    assert len(feature_lines) > 0

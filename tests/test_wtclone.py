import os
import subprocess
import pytest

def test_wtclone_basic(temp_dir, remote_repo, scripts_dir):
    """Test that wtclone.sh clones a repo correctly."""
    wtclone_script = os.path.join(scripts_dir, "wtclone.sh")

    # Run wtclone.sh
    # Usage: wtclone REPO_URL [DIR_NAME]
    target_dir_name = "my-project"
    cmd = [wtclone_script, remote_repo, target_dir_name]

    # Run in the temp dir
    subprocess.check_call(cmd, cwd=temp_dir)

    project_path = os.path.join(temp_dir, target_dir_name)

    # Check directory exists
    assert os.path.exists(project_path)

    # Check .bare directory exists
    assert os.path.exists(os.path.join(project_path, ".bare"))

    # Check .git file exists and points to .bare
    git_file = os.path.join(project_path, ".git")
    assert os.path.exists(git_file)
    with open(git_file, "r") as f:
        content = f.read().strip()
        assert content == "gitdir: ./.bare"

    # Check that the main worktree was created
    # The script tries to determine the default branch.
    # In our fixture we pushed 'master'.
    # Note: `git branch --show-current` in the bare repo might behave specifically.
    # The script does:
    # cd "$name"
    # git clone --bare "$url" .bare
    # ...
    # git fetch origin
    # main_branch=$(git branch --show-current)
    # git worktree add "$main_branch"

    # In a bare repo, git branch --show-current usually returns empty or the HEAD.
    # Wait, the script does:
    # git clone --bare "$url" .bare
    # echo "gitdir: ./.bare" > .git
    # ...
    # main_branch=$(git branch --show-current)
    # This runs in the project_path context where .git -> .bare.
    # Since .bare is bare, HEAD usually points to master (or whatever remote HEAD was).

    # Let's verify 'master' directory exists
    master_path = os.path.join(project_path, "master")
    assert os.path.exists(master_path)
    assert os.path.exists(os.path.join(master_path, "README.md"))

def test_wtclone_custom_name(temp_dir, remote_repo, scripts_dir):
    """Test wtclone.sh with default directory name."""
    wtclone_script = os.path.join(scripts_dir, "wtclone.sh")

    # Run wtclone.sh without target name
    cmd = [wtclone_script, remote_repo]
    subprocess.check_call(cmd, cwd=temp_dir)

    # The default name is the basename of the repo url
    # remote_repo path ends with remote-repo.git
    expected_name = "remote-repo"
    project_path = os.path.join(temp_dir, expected_name)

    assert os.path.exists(project_path)
    assert os.path.exists(os.path.join(project_path, ".bare"))
    assert os.path.exists(os.path.join(project_path, "master"))

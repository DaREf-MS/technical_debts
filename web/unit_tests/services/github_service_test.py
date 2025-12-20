# test_github_service.py
import os
from pathlib import Path

from src.services import github_service

# ---- ensure_local_repo tests ----
def test_ensure_local_repo_clones_when_missing(tmp_path, monkeypatch):
    # Use a temp dir as the cache root so we don't touch real disk
    monkeypatch.setenv("REPO_CACHE_DIR", str(tmp_path))

    calls = []

    def fake_run(cmd, check, stdout=None, stderr=None):
        # record the command so we can assert on it
        calls.append(cmd)

    # Patch subprocess.run used inside github_service
    monkeypatch.setattr(github_service.subprocess, "run", fake_run)

    # ---- act ----
    repo_path = github_service.ensure_local_repo("my-owner", "my-repo")

    # ---- assert ----
    # 1) path is under our cache dir with the expected naming
    expected_path = tmp_path / "my-owner__my-repo"
    assert Path(repo_path) == expected_path

    # 2) it attempted a clone with --no-checkout
    assert len(calls) == 1
    cmd = calls[0]
    # starts with: git clone --no-checkout
    assert cmd[0:3] == ["git", "clone", "--no-checkout"]
    # contains the repo URL and target path
    assert github_service.remote_url("my-owner", "my-repo") in cmd
    assert str(expected_path) in cmd



# ---- ensure_local_repo tests ----
def test_ensure_local_repo_uses_existing_repo(tmp_path, monkeypatch):
    # Use test directory as fake cache root
    monkeypatch.setenv("REPO_CACHE_DIR", str(tmp_path))

    repo_path = tmp_path / "my-owner__my-repo"
    git_dir = repo_path / ".git"

    # Create the folder and fake .git so it's seen as a repo
    git_dir.mkdir(parents=True)

    calls = []

    class DummyResult:
        def __init__(self, stdout=""):
            self.stdout = stdout

    # Patch subprocess.run to track if clone/run gets called
    def fake_run(*args, **kwargs):
        cmd = args[0]
        calls.append(cmd)
        # When check_output calls this, it expects .stdout to exist
        return DummyResult(stdout="https://github.com/my-owner/my-repo.git\n")

    monkeypatch.setattr(github_service.subprocess, "run", fake_run)

    # ---- act ----
    result_path = github_service.ensure_local_repo("my-owner", "my-repo")

    # ---- assert ----
    # Should return the existing directory
    assert result_path == str(repo_path)

    # Should NOT call 'git clone'
    for cmd in calls:
        assert "clone" not in cmd


# ---- safe_walk_source_files tests ----
def test_safe_walk_source_files_yields_supported_extensions(tmp_path):
    # Create a fake repo structure
    root = tmp_path / "repo"
    root.mkdir()

    # Supported files
    (root / "main.py").write_text("print('hello')")
    (root / "lib.cpp").write_text("int main(){return 0;}")
    (root / "index.js").write_text("console.log('x')")

    # Unsupported file
    (root / "readme.md").write_text("# doc")

    yielded = list(github_service.safe_walk_source_files(str(root)))
    names = {name for _, name in yielded}

    assert "main.py" in names
    assert "lib.cpp" in names
    assert "index.js" in names
    assert "readme.md" not in names


def test_safe_walk_source_files_skips_git_directory(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()

    # Normal supported file
    (root / "main.py").write_text("print('hello')")

    # Inside .git should be ignored
    git_dir = root / ".git"
    git_dir.mkdir()
    (git_dir / "ignored.py").write_text("print('ignore')")

    yielded = list(github_service.safe_walk_source_files(str(root)))
    names = {name for _, name in yielded}

    assert "main.py" in names
    assert "ignored.py" not in names


def test_safe_walk_source_files_handles_multiple_dots(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()

    # Supported with multiple dots
    (root / "module.test.util.py").write_text("x=1")
    # Unsupported with multiple dots
    (root / "archive.tar.gz").write_text("binary")

    yielded = list(github_service.safe_walk_source_files(str(root)))
    names = {name for _, name in yielded}

    assert "module.test.util.py" in names
    assert "archive.tar.gz" not in names

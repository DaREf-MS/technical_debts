# metrics_service_test.py

import pytest
from unittest.mock import Mock

from src.services.metrics_service import calculate_bug_counts_in_range
from src.services import metrics_service
from src.services.metrics_service import MetricsClass


# ---------- Test Fixtures ----------
@pytest.fixture
def mock_repo():
    repo = Mock()
    repo.owner = "test-owner"
    repo.name = "test-repo"
    return repo

@pytest.fixture
def mock_branch():
    branch = Mock()
    branch.name = "main"
    return branch

@pytest.fixture
def mock_commit():
    commit = Mock()
    commit.id = 42
    commit.sha = "abc123"
    return commit

@pytest.fixture
def mock_db_session():
    session = Mock()
    session.added = []
    session.commit_called = False
    session.rollback_called = False
    
    def add_side_effect(obj):
        session.added.append(obj)
    
    def commit_side_effect():
        session.commit_called = True
        
    def rollback_side_effect():
        session.rollback_called = True
    
    session.add.side_effect = add_side_effect
    session.commit.side_effect = commit_side_effect
    session.rollback.side_effect = rollback_side_effect
    return session

@pytest.fixture
def mock_services(mock_repo, mock_branch):
    """Set up all the common service mocks."""
    services = {}
    
    # Repository service
    services['repository'] = Mock()
    services['repository'].get_repository_by_repository_id.return_value = mock_repo
    
    # Branch service
    services['branch'] = Mock()
    services['branch'].get_branch_by_branch_id.return_value = mock_branch
    
    # GitHub service
    services['github'] = Mock()
    services['github'].get_commits_in_date_range.return_value = [
        {"sha": "abc", "message": "fix bug"},
        {"sha": "def", "message": "refactor"},
    ]
    services['github'].fetch_files.return_value = [
        ("file1.py", "code1"),
        ("file2.py", "code2"),
    ]
    
    return services

@pytest.fixture
def sample_commits():
    return [
        {"message": "Bug: something is broken"},
        {"message": "FIX: capital letters should count"},
        {"message": "This fixes the previous issue"},
        {"message": "We finally fixed the login"},
        {"message": "Random commit without keyword"},
    ]

# ---------- Tests for MetricsClass ----------
def test_get_commits_in_date_range_uses_services(monkeypatch, mock_services):
    """Test that get_commits_in_date_range calls the right services with correct parameters."""
    # Patch only existing services
    for service_name, mock_service in mock_services.items():
        monkeypatch.setattr(metrics_service, f"{service_name}_service", mock_service)

    metrics = MetricsClass(repo_id=123, branch_id=456)
    start, end = "01/01/2025 00:00", "31/01/2025 23:59"

    result = metrics.get_commits_in_date_range(start, end)

    # Verify result
    assert result == [
        {"sha": "abc", "message": "fix bug"},
        {"sha": "def", "message": "refactor"},
    ]
    
    # Verify service calls
    mock_services['repository'].get_repository_by_repository_id.assert_called_once_with(123)
    mock_services['branch'].get_branch_by_branch_id.assert_called_once_with(456)
    mock_services['github'].get_commits_in_date_range.assert_called_once_with(
        "test-owner", "test-repo", "main", start, end
    )


# ---------- Tests for calculate_bug_counts_in_range ----------
class TestCalculateBugCountsInRange:
    
    @pytest.mark.parametrize("commits,expected", [
        ([], {"total": 0}),
        ([{"message": "Refactor code"}, {"message": "Add new feature"}], {"total": 0}),
        ([{}, {"message": "fix small bug"}, {"msg": "wrong key"}], {"total": 1}),
    ])
    def test_edge_cases(self, commits, expected):
        """Test edge cases: empty list, no matches, missing keys."""
        assert calculate_bug_counts_in_range(commits) == expected

    def test_counts_all_matching_commits(self, sample_commits):
        """Test that all bug/fix related commits are counted."""
        result = calculate_bug_counts_in_range(sample_commits)
        assert result == {"total": 4}

    @pytest.mark.parametrize("commits,expected", [
        ([{"message": "Bug: something happened"}, {"message": "FIX this today"}], 2),
        ([{"message": "this fixes issue #22"}, {"message": "login flow fixed"}], 2),
        ([{"message": "BUG found"}, {"message": "fIxEs logout"}], 2),
    ])
    def test_keyword_variants(self, commits, expected):
        """Test different bug/fix keyword variants and case insensitivity."""
        result = calculate_bug_counts_in_range(commits)
        assert result["total"] == expected


# ---------- Tests for ensure_metric_snapshot ----------
class TestEnsureMetricSnapshot:
    def _setup_existing_data_mocks(self, monkeypatch, mock_services, mock_commit, mock_db_session):
        """Setup mocks for when data already exists."""
        # Mock existing data queries
        mock_entity_count = Mock()
        mock_entity_count.query.filter_by.return_value.all.return_value = ["existing"]
        
        mock_complexity_count = Mock() 
        mock_complexity_count.query.filter_by.return_value.first.return_value = "existing"
        
        # Services that shouldn't be called
        github_service_mock = Mock()
        calc_identifiable_mock = Mock(side_effect=AssertionError("Should not be called"))
        calc_complexity_mock = Mock(side_effect=AssertionError("Should not be called"))
        
        # Mock DB
        mock_db = Mock()
        mock_db.session = mock_db_session
        
        # Apply patches
        patches = {
            "IdentifiableEntityCount": mock_entity_count,
            "ComplexityCount": mock_complexity_count,
            "github_service": github_service_mock,
            "calculate_identifiable_identities_analysis": calc_identifiable_mock,
            "calculate_cyclomatic_complexity_analysis": calc_complexity_mock,
            "db": mock_db,
        }
        
        for attr, mock_obj in patches.items():
            monkeypatch.setattr(metrics_service, attr, mock_obj)
            
        for service_name, mock_service in mock_services.items():
            monkeypatch.setattr(metrics_service, f"{service_name}_service", mock_service)
            
        return github_service_mock

    def test_returns_early_when_snapshot_already_exists(self, monkeypatch, mock_services, mock_commit, mock_db_session):
        """Test that method returns early when snapshot already exists."""
        github_mock = self._setup_existing_data_mocks(monkeypatch, mock_services, mock_commit, mock_db_session)
        
        metrics = MetricsClass(repo_id=123, branch_id=456)
        result = metrics.ensure_metric_snapshot(mock_commit)

        assert result is None
        github_mock.fetch_files.assert_not_called()
        assert not mock_db_session.added
        assert not mock_db_session.commit_called

    def _setup_new_snapshot_mocks(self, monkeypatch, mock_services, mock_commit, mock_db_session):
        """Setup mocks for when no snapshot exists and needs to be created."""
        # Mock empty data queries
        mock_entity_count = Mock()
        mock_entity_count.query.filter_by.return_value.all.return_value = []
        mock_entity_count.side_effect = lambda *args, **kwargs: Mock(**kwargs)
        
        mock_complexity_count = Mock()
        mock_complexity_count.query.filter_by.return_value.first.return_value = None
        mock_complexity_count.side_effect = lambda *args, **kwargs: Mock(**kwargs)
        
        # Mock entities
        entities = [Mock(id="e1", name="PASSWORD"), Mock(id="e2", name="API_KEY")]
        mock_entity_service = Mock()
        mock_entity_service.get_all_identifiable_entities.return_value = entities
        
        # Mock file service
        mock_file_service = Mock()
        mock_file_service.create_file.side_effect = lambda name, commit_id: Mock(id=f"file-{name}", name=name, commit_id=commit_id)
        
        # Mock analysis functions
        def mock_calc_identifiable(file, code):
            if file.name == "file1.py":
                return [
                    {"file": file.name, "start_line": 10, "entity_name": "PASSWORD"},
                    {"file": file.name, "start_line": 20, "entity_name": "PASSWORD"},
                ]
            return [{"file": file.name, "start_line": 5, "entity_name": "API_KEY"}]
    
        def mock_calc_complexity(file, code):
            complexity = 3 if file.name == "file1.py" else 7
            return [{
                "file": file.name,
                "function": f"f{1 if file.name == 'file1.py' else 2}",
                "start_line": 1,
                "cyclomatic_complexity": complexity,
            }]
        
        # Mock DB
        mock_db = Mock()
        mock_db.session = mock_db_session
        
        # Apply patches
        patches = {
            "IdentifiableEntityCount": mock_entity_count,
            "ComplexityCount": mock_complexity_count,
            "identifiable_entity_service": mock_entity_service,
            "file_service": mock_file_service,
            "calculate_identifiable_identities_analysis": mock_calc_identifiable,
            "calculate_cyclomatic_complexity_analysis": mock_calc_complexity,
            "db": mock_db,
        }
        
        for attr, mock_obj in patches.items():
            monkeypatch.setattr(metrics_service, attr, mock_obj)
            
        for service_name, mock_service in mock_services.items():
            monkeypatch.setattr(metrics_service, f"{service_name}_service", mock_service)

    def test_creates_metrics_when_no_snapshot_exists(self, monkeypatch, mock_services, mock_commit, mock_db_session):
        """Test that metrics are created when no snapshot exists."""
        self._setup_new_snapshot_mocks(monkeypatch, mock_services, mock_commit, mock_db_session)
        
        metrics = MetricsClass(repo_id=123, branch_id=456)
        result = metrics.ensure_metric_snapshot(mock_commit)

        assert result is None
        
        # Verify services were called
        mock_services['github'].fetch_files.assert_called_once_with("test-owner", "test-repo", "abc123")
        assert mock_db_session.commit_called
        assert not mock_db_session.rollback_called
        assert len(mock_db_session.added) > 0

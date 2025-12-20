import uuid
from datetime import datetime, timezone

from src.models import db
from src.models.model import *

import src.services.repository_service as repository_service
import src.services.branch_service as branch_service
import src.services.github_service as github_service
import src.services.commit_service as commit_service


class ProjectSearchHandler:
    """
    A handler class for project search operations with repository and branch context.
    """
    
    def __init__(self, repository, branch, start_date=None, end_date=None):
        """
        Initialize the ProjectSearchHandler with repository, branch, and optional date range.
        
        Args:
            repository: Repository object or repository ID
            branch: Branch object or branch ID
            start_date: Start date for search operations (str or datetime)
            end_date: End date for search operations (str or datetime)
        """
        self.repository = repository
        self.branch = branch
        self.start_date = start_date
        self.end_date = end_date
        
        # Commit-related attributes - will be populated when commits are retrieved
        self.commits_in_range = None
        self.commit_ids = None
        self.commit_lookup = None
        self.missing_commits = None
    
    def get_repository_info(self):
        """
        Get repository information.
        
        Returns:
            dict: Repository information
        """
        if isinstance(self.repository, str):
            # If repository is an ID, fetch the repository object
            repo = repository_service.get_repository_by_repository_id(self.repository)
            return repo.as_dict() if repo else None
        elif hasattr(self.repository, 'as_dict'):
            # If repository is an object with as_dict method
            return self.repository.as_dict()
        else:
            # If repository is already a dict or other format
            return self.repository
    
    def get_branch_info(self):
        """
        Get branch information.
        
        Returns:
            dict: Branch information
        """
        if isinstance(self.branch, str):
            # If branch is an ID, fetch the branch object
            branch_obj = branch_service.get_branch_by_branch_id(self.branch)
            return branch_obj.as_dict() if branch_obj and hasattr(branch_obj, 'as_dict') else branch_obj
        elif hasattr(self.branch, 'as_dict'):
            # If branch is an object with as_dict method
            return self.branch.as_dict()
        else:
            # If branch is already a dict or other format
            return self.branch
    
    def get_search_context(self):
        """
        Get the full search context including repository, branch, and date range information.
        
        Returns:
            dict: Combined repository, branch, and date context
        """
        return {
            "repository": self.get_repository_info(),
            "branch": self.get_branch_info(),
            "start_date": self.start_date,
            "end_date": self.end_date,
            "commits_in_range": self.commits_in_range,
            "commit_ids": self.commit_ids,
            "missing_commits": self.missing_commits
        }
    
    def get_commits_in_date_range(self):
        """
        Get commits in the specified date range for the repository and branch.
        
        Returns:
            list: List of commits in the date range
            
        Raises:
            ValueError: If start_date or end_date is not set
            Exception: If repository or branch information cannot be retrieved
        """
        if not self.start_date or not self.end_date:
            raise ValueError("Both start_date and end_date must be set to get commits in date range")
        
        # Get repository information
        repo_info = self.get_repository_info()
        if not repo_info:
            raise Exception("Repository information could not be retrieved")
        
        # Get branch information
        branch_info = self.get_branch_info()
        if not branch_info:
            raise Exception("Branch information could not be retrieved")
        
        # Extract owner and name from repository
        if isinstance(repo_info, dict):
            repo_owner = repo_info.get('owner')
            repo_name = repo_info.get('name')
        else:
            # Try to get from repository object if it has these attributes
            repo_owner = getattr(self.repository, 'owner', None)
            repo_name = getattr(self.repository, 'name', None)
        
        # Extract branch name
        if isinstance(branch_info, dict):
            branch_name = branch_info.get('name')
        else:
            # Try to get from branch object if it has name attribute
            branch_name = getattr(self.branch, 'name', None)
        
        if not repo_owner or not repo_name or not branch_name:
            raise Exception("Could not extract required repository owner, name, or branch name")
        
        # Get commits in the date range using github_service
        commits_in_range = github_service.get_commits_in_date_range(
            repo_owner, repo_name, branch_name, self.start_date, self.end_date
        )
        
        # Store commits as attribute
        self.commits_in_range = commits_in_range
        
        return commits_in_range
    
    def process_commits_for_database(self):
        """
        Get commit IDs and build lookup for commits in the date range.
        Processes commits from the date range and creates mapping to database records.
        
        Returns:
            tuple: (commit_ids, commit_lookup, missing_commits)
                - commit_ids: List of commit IDs found in database
                - commit_lookup: Dictionary mapping commit_id to commit info
                - missing_commits: List of commit SHAs not found in database
        """
        # Ensure we have commits_in_range (get them if not already retrieved)
        if self.commits_in_range is None:
            self.get_commits_in_date_range()
        
        # Get commit IDs for the commits in range
        commit_ids = []
        commit_lookup = {}
        missing_commits = []
        
        for commit_data in self.commits_in_range:
            commit = commit_service.get_commit_by_sha(commit_data["sha"])
            if commit:
                commit_ids.append(commit.id)
                commit_lookup[commit.id] = {
                    "sha": commit.sha,
                    "date": commit.date,
                    "author": commit.author,
                    "message": commit.message
                }
            else:
                missing_commits.append(commit_data["sha"])
        
        # Store as attributes
        self.commit_ids = commit_ids
        self.commit_lookup = commit_lookup
        self.missing_commits = missing_commits
        
        return commit_ids, commit_lookup, missing_commits
    
    def __repr__(self):
        """
        String representation of the ProjectSearchHandler.
        
        Returns:
            str: String representation
        """
        repo_info = self.get_repository_info()
        branch_info = self.get_branch_info()
        
        repo_name = repo_info.get('name') if isinstance(repo_info, dict) else str(self.repository)
        branch_name = branch_info.get('name') if isinstance(branch_info, dict) else str(self.branch)
        
        date_info = ""
        if self.start_date or self.end_date:
            date_info = f", start_date='{self.start_date}', end_date='{self.end_date}'"
        
        return f"ProjectSearchHandler(repository='{repo_name}', branch='{branch_name}'{date_info})"
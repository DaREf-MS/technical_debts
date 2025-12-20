import uuid
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from flask import current_app

from src.models import db
from src.models.model import *

from lizard import analyze_file
import src.services.function_service as function_service
import src.services.complexity_service as complexity_service
import src.services.identifiable_entity_service as identifiable_entity_service
import src.services.github_service as github_service
import src.services.repository_service as repository_service
import src.services.branch_service as branch_service
import src.services.commit_service as commit_service
import src.services.file_service as file_service
import re
from src.controllers.duplication_controller import DuplicationController

# Thread-safe database operation lock
_db_lock = Lock()


def _process_single_file_for_metrics(filename, code, commit_id, identifiable_entities, app):
    """
    Process a single file for metrics analysis in parallel.
    
    Args:
        filename: Name of the file
        code: Source code content
        commit_id: ID of the commit
        identifiable_entities: List of identifiable entities to search for
        app: Flask application instance for context
        
    Returns:
        dict: Contains file object, analysis results, and metrics
    """
    with app.app_context():
        # Create file record (thread-safe)
        with _db_lock:
            file = file_service.create_file(filename, commit_id)
            
            # Check if duplications already exist for this specific file
            existing_file_duplications = (
                db.session.query(Duplication)
                .filter(Duplication.file_id == file.id)
                .first()
            )
        
        needs_duplication = not existing_file_duplications
        
        # Calculate identifiable entities for this file
        identifiable_identities_analysis = calculate_identifiable_identities_analysis(file, code)
        
        # Calculate complexity for this file
        complexity_analysis = calculate_cyclomatic_complexity_analysis(file, code)
        
        # Compute metrics
        file_complexity = sum(c["cyclomatic_complexity"] for c in complexity_analysis)
        file_function_count = len(complexity_analysis)
        
        return {
            'file': file,
            'needs_duplication': needs_duplication,
            'identifiable_identities': identifiable_identities_analysis,
            'complexity_analysis': complexity_analysis,
            'total_complexity': file_complexity,
            'function_count': file_function_count
        }


class MetricsClass:
    repo = None
    branch = None

    def __init__(self, repo_id, branch_id):
        self.repo = repository_service.get_repository_by_repository_id(repo_id)
        self.branch = branch_service.get_branch_by_branch_id(branch_id)

    def get_commits_in_date_range(self, start_date, end_date):
        commits_in_range = github_service.get_commits_in_date_range(
            self.repo.owner, self.repo.name, self.branch.name, start_date, end_date
        )

        return commits_in_range

    def ensure_metric_snapshot(self, commit_to_check):
        # check if there is a snapshot of the count of identifiable identities
        existing_counts = IdentifiableEntityCount.query.filter_by(commit_id=commit_to_check.id).all()
        existing_complexity = ComplexityCount.query.filter_by(commit_id=commit_to_check.id).first()

        if existing_counts and existing_complexity:
            # snapshots already calculated for this commit
            return

        try:
            # the snapshot has not yet been calculated, so we calculate it
            remote_files = github_service.fetch_files(self.repo.owner, self.repo.name, commit_to_check.sha)

            # Initialize counters for each identifiable entity type
            identifiable_entities = identifiable_entity_service.get_all_identifiable_entities()
            entity_totals = {}
            for entity in identifiable_entities:
                entity_totals[entity.id] = {"name": entity.name, "count": 0}

            # Initialize complexity tracking
            total_complexity = 0
            function_count = 0
            files_for_duplication = []

            # Get Flask app for context in threads
            try:
                app = current_app._get_current_object()
            except RuntimeError:
                # Fallback if not in app context
                from src.app import app as flask_app
                app = flask_app

            # Process files in parallel using ThreadPoolExecutor
            max_workers = min(8, len(remote_files)) if remote_files else 1
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all file processing tasks
                future_to_file = {
                    executor.submit(_process_single_file_for_metrics, filename, code, commit_to_check.id, identifiable_entities, app): (filename, code)
                    for filename, code in remote_files
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_file):
                    try:
                        result = future.result()
                        
                        # Accumulate entity counts
                        for entity_analysis in result['identifiable_identities']:
                            entity_name = entity_analysis["entity_name"]
                            for entity_id, entity_info in entity_totals.items():
                                if entity_info["name"] == entity_name:
                                    entity_totals[entity_id]["count"] += 1
                                    break
                        
                        # Accumulate complexity metrics
                        total_complexity += result['total_complexity']
                        function_count += result['function_count']
                        
                        # Track files needing duplication analysis
                        if result['needs_duplication']:
                            files_for_duplication.append(result['file'])
                            
                    except Exception as e:
                        filename, code = future_to_file[future]
                        print(f"Error processing file {filename}: {str(e)}")

            # Calculate code duplications for files that don't have them yet
            if files_for_duplication:
                try:
                    # Ensure local repository is available
                    repo_dir = github_service.ensure_local_repo(self.repo.owner, self.repo.name)
                    
                    # Get duplication controller and run analysis
                    duplication_controller = DuplicationController.singleton()
                    duplication_controller.find_duplications("pmd_cpd", repo_dir, files_for_duplication)
                except Exception as e:
                    print("error calculating duplication")

            # Store the entity counts in the database
            if not existing_counts:
                for entity_id, entity_info in entity_totals.items():
                    db.session.add(IdentifiableEntityCount(
                        id = str(uuid.uuid4()),
                        identifiable_entity_id = entity_id,
                        commit_id = commit_to_check.id,
                        count = entity_info["count"],
                    ))

            # Store the complexity summary in the database
            if not existing_complexity:
                average_complexity = total_complexity / function_count if function_count > 0 else 0
                db.session.add(ComplexityCount(
                    id = str(uuid.uuid4()),
                    commit_id = commit_to_check.id,
                    total_complexity = total_complexity,
                    function_count = function_count,
                    average_complexity = average_complexity,
                ))

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            raise


def calculate_cyclomatic_complexity_analysis(file, code):
    
    cyclomatic_complexity_analysis = []
    analysis = analyze_file.analyze_source_code(file.name, code)
    for func in analysis.function_list:
        # ensure function record exists
        function = function_service.get_function_by_name_and_file(func.name, file.id)
        if not function:
            function = function_service.create_function(func.name, func.start_line, file.id)

        # update or create complexity
        existing_complexity = Complexity.query.filter_by(function_id=function.id).first()

        if existing_complexity:
            existing_complexity.value = func.cyclomatic_complexity
            db.session.commit()
        else:
            complexity_service.create_complexity(func.cyclomatic_complexity, function.id)

        cyclomatic_complexity_analysis.append({
            "file": file.name,
            "function": func.name,
            "start_line": func.start_line,
            "cyclomatic_complexity": func.cyclomatic_complexity
        })

    return cyclomatic_complexity_analysis


def calculate_identifiable_identities_analysis(file, code):
    identifiable_entity_analysis = []

    # get all the identifiable identities to search for
    identities = identifiable_entity_service.get_all_identifiable_entities()
    for identity in identities:
        # search the file for the identity (e.g. <TODO>, <FIXME>)
        found_identities = identifiable_entity_service.search_identifable_entity(code, identity.name)

        # link the found identity to the file it was found in
        for line in found_identities:
            identifiable_entity_service.create_file_entity(identity.id, file.id, line)

            identifiable_entity_analysis.append({
                "file": file.name,
                "start_line": line,
                "entity_name": identity.name,
            })

    return identifiable_entity_analysis


# get all the commits in the specified range of date
# commits_in_range = github_service.get_commits_in_date_range(repo.owner, repo.name, branch.name, start_date, end_date)


def get_identifiable_entity_counts_for_commit(commit_id):
    """
    Count the number of times an identifiable identity for each one
    
    Args:
        commit_id (str): The commit ID
        
    Returns:
        dict: Dictionary with entity names as keys and counts as values
    """
    counts = IdentifiableEntityCount.query.filter_by(commit_id=commit_id).all()
    result = {}
    
    for count in counts:
        entity = IdentifiableEntity.query.get(count.identifiable_entity_id)
        if entity:
            result[entity.name] = count.count
    
    return result


def get_complexity_count_for_commit(commit_id):
    """
    Get the complexity counts for multiple commits.
    
    Args:
        commit_ids (list): List of commit IDs
        
    Returns:
        dict: Dictionary with commit_id as keys and complexity data as values
    """

    complexity_count = ComplexityCount.query.filter_by(commit_id=commit_id).first()

    return {
        "total_complexity": complexity_count.total_complexity,
        "function_count": complexity_count.function_count,
        "average_complexity": complexity_count.average_complexity
    }


LINKED_BUGS_KEYWORDS = re.compile(
    r"""
    \b(
        bug|bugs|bugfix|bugfixes|
        fix|fixes|fixed|hotfix|
        issue|issues|
        error|errors|
        crash|crashes|
        correction|corrected|
        corrige|corrigé|répare|réparé|résout
    )\b
    """,
    re.IGNORECASE | re.VERBOSE,
)


def calculate_bug_counts_in_range(commits_in_range):
    """
    Receives a list of commits (each being a dict with a 'message' field)
    Counts how many commit messages contain 'bug' or 'fix' (case-insensitive)
    Returns a dict like: {"total": 7}
    """
    linked_bugs = {"total": 0}

    if not commits_in_range:
        return linked_bugs

    count = 0
    for commit in commits_in_range:
        message = commit.get("message", "") or ""
        message = message.strip().lower()

        # Only count meaningful bug-related terms, not debug/prefix/etc.
        if LINKED_BUGS_KEYWORDS.search(message):
            count += 1

    linked_bugs["total"] = count    

    return linked_bugs


def calculate_debt_evolution(repo_id, branch_id, start_date, end_date, task_id=None):
    """
    Calculate the evolution of technical debt (identifiable entities) over time.
    
    Args:
        repo_id (str): Repository ID
        branch_id (str): Branch ID
        start_date (str): Start date in format "dd/mm/YYYY HH:MM"
        end_date (str): End date in format "dd/mm/YYYY HH:MM"
        task_id (str, optional): Task ID for progress reporting
        
    Returns:
        list: List of debt evolution data points
    """
    from src.services.task_manager import task_manager
    
    # Start timing the entire function
    function_start_time = time.time()
    print(f"[TIMING] calculate_debt_evolution started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    debt_evolution = []

    try:
        if task_id:
            task_manager.update_progress(task_id, 5, "Fetching commits", "Loading commits in date range...")
        
        # Time: Creating MetricsClass instance
        step_start = time.time()
        metrics_class = MetricsClass(repo_id, branch_id)
        print(f"[TIMING] MetricsClass initialization took {time.time() - step_start:.2f}s")

        # Time: Fetching commits
        step_start = time.time()
        commits_in_range = metrics_class.get_commits_in_date_range(start_date, end_date)
        print(f"[TIMING] Fetching {len(commits_in_range)} commits took {time.time() - step_start:.2f}s")

        # Initialize timing statistics
        timing_stats = defaultdict(list)
        total_iterations = len(commits_in_range)
        
        if task_id:
            task_manager.update_progress(task_id, 10, "Processing commits", f"Analyzing {total_iterations} commits...")

        # Time: Processing all commits
        all_commits_start = time.time()
        
        for i, found_commit in enumerate(commits_in_range, 1):
            iteration_start = time.time()
            
            # Calculate progress (10% to 90% of the task)
            progress = 10 + int((i / total_iterations) * 80)
            
            # Get SHA from commit (handle both dict and object)
            commit_sha = found_commit.get('sha') if isinstance(found_commit, dict) else found_commit.sha
            
            if task_id:
                task_manager.update_progress(
                    task_id, 
                    progress, 
                    f"Processing commit {i}/{total_iterations}",
                    f"Analyzing commit {commit_sha[:7]}..."
                )
            
            # 1 - Create commit in database, if missing
            step_start = time.time()
            commit = commit_service.ensure_commit_exists_by_sha(found_commit, branch_id)
            timing_stats['ensure_commit'].append(time.time() - step_start)

            # 2 - Calculate metrics, if the commit was missing
            step_start = time.time()
            metrics_class.ensure_metric_snapshot(commit)
            timing_stats['ensure_metric_snapshot'].append(time.time() - step_start)

            # Get entity counts for current commit, if missing
            step_start = time.time()
            entity_counts = get_identifiable_entity_counts_for_commit(commit.id)
            print(f"[DEBUG] Commit {commit.sha[:7]} - Entity counts: {entity_counts}")
            total_identifiable_entities = 0
            for count in entity_counts.values():
                total_identifiable_entities += count
            timing_stats['get_entity_counts'].append(time.time() - step_start)

            # Get complexity counts for current commit, if missing
            step_start = time.time()
            complexity_count = get_complexity_count_for_commit(commit.id)
            linked_bugs = calculate_bug_counts_in_range(commits_in_range)
            timing_stats['get_complexity_and_bugs'].append(time.time() - step_start)

            step_start = time.time()
            files = File.query.filter_by(commit_id=commit.id).all()
            file_ids = [f.id for f in files]
            total_number_duplications = Duplication.query.filter(
                Duplication.file_id.in_(file_ids)
            ).count()
            timing_stats['get_duplications'].append(time.time() - step_start)

            # Build result data
            step_start = time.time()
            debt_evolution.append({
                "commit_sha": commit.sha,
                "commit_date": commit.date.isoformat() if commit.date else None,
                "commit_author": commit.author,
                "commit_message": commit.message,
                "total_identifiable_entities": total_identifiable_entities,
                "entity_breakdown": entity_counts,
                "complexity_data": complexity_count,
                "linked_bugs_total": linked_bugs["total"],
                "total_number_duplications": total_number_duplications,
            })
            timing_stats['build_result'].append(time.time() - step_start)
            
            iteration_time = time.time() - iteration_start
            timing_stats['total_iteration'].append(iteration_time)

        all_commits_time = time.time() - all_commits_start
        print(f"[TIMING] Processing all {total_iterations} commits took {all_commits_time:.2f}s (avg {all_commits_time/max(total_iterations, 1):.2f}s per commit)")

        if task_id:
            task_manager.update_progress(task_id, 95, "Finalizing", "Sorting and preparing results...")

        # Sort by date
        step_start = time.time()
        debt_evolution.sort(key=lambda x: x["commit_date"] or "")
        print(f"[TIMING] Sorting results took {time.time() - step_start:.2f}s")

        # Print detailed timing statistics
        print("\n[TIMING] Detailed statistics per commit:")
        for operation, times in timing_stats.items():
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
                print(f"  {operation}: avg={avg_time:.3f}s, min={min_time:.3f}s, max={max_time:.3f}s, total={sum(times):.2f}s")

        #Bug: this line breaks the a part in debt_evolution.js because it is not json
        #debt_evolution.append({"linked_bugs_total": linked_bugs["total"]})
    except Exception as e:
        print(f"Error calculating debt evolution: {str(e)}")
        raise
    finally:
        total_time = time.time() - function_start_time
        print(f"[TIMING] calculate_debt_evolution TOTAL TIME: {total_time:.2f}s ({total_time/60:.2f} minutes)")
        print(f"[TIMING] calculate_debt_evolution ended at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    return debt_evolution

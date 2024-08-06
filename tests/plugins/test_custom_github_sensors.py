import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
from github.GithubException import GithubException, RateLimitExceededException
from github_sensors import GitHubPRMergedSensor, GitHubFileChangedSensor
from airflow.models import DAG
from airflow.utils.dates import days_ago

# Create a sample DAG for testing purposes
test_dag = DAG(
    'test_dag',
    description='Test DAG for GitHub sensors',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
)

@pytest.fixture
def github_mock():
    """Fixture for mocking GitHub API."""
    with patch('github.Github') as mock_github:
        yield mock_github

@pytest.fixture
def sensor_setup():
    """Fixture for setting up common parameters for sensors."""
    owner = 'username'
    repo = 'repo_name'
    branch = 'main'
    file_path = 'path/to/your/file.txt'
    http_conn_id = 'my_github_connection'
    return owner, repo, branch, file_path, http_conn_id

def test_pr_merged_sensor_success(github_mock, sensor_setup):
    """Test that the GitHubPRMergedSensor detects a merged PR within 24 hours."""
    owner, repo, _, _, http_conn_id = sensor_setup
    mock_github = github_mock.return_value
    mock_repo = mock_github.get_repo.return_value

    # Mock a pull request with a merged_at timestamp within the last 24 hours
    mock_pr = MagicMock()
    mock_pr.merged_at = datetime.now(timezone.utc) - timedelta(hours=1)
    mock_repo.get_pulls.return_value = [mock_pr]

    # Create the sensor instance
    sensor = GitHubPRMergedSensor(
        task_id='check_any_pr_merged',
        owner=owner,
        repo=repo,
        poke_interval=60,
        http_conn_id=http_conn_id,
        dag=test_dag,
        retry_attempts=3,
        retry_delay=5,
        timeout=10,
    )

    # Execute the poke method and assert the result
    result = sensor.poke(None)
    assert result is True, "The sensor should return True when a PR has been merged within 24 hours."

def test_pr_merged_sensor_no_pr_merged(github_mock, sensor_setup):
    """Test that the GitHubPRMergedSensor returns False if no PRs have been merged within 24 hours."""
    owner, repo, _, _, http_conn_id = sensor_setup
    mock_github = github_mock.return_value
    mock_repo = mock_github.get_repo.return_value

    # Mock a pull request with a merged_at timestamp older than 24 hours
    mock_pr = MagicMock()
    mock_pr.merged_at = datetime.now(timezone.utc) - timedelta(days=2)
    mock_repo.get_pulls.return_value = [mock_pr]

    # Create the sensor instance
    sensor = GitHubPRMergedSensor(
        task_id='check_any_pr_merged',
        owner=owner,
        repo=repo,
        poke_interval=60,
        http_conn_id=http_conn_id,
        dag=test_dag,
        retry_attempts=3,
        retry_delay=5,
        timeout=10,
    )

    # Execute the poke method and assert the result
    result = sensor.poke(None)
    assert result is False, "The sensor should return False when no PRs have been merged within 24 hours."

def test_file_changed_sensor_success(github_mock, sensor_setup):
    """Test that the GitHubFileChangedSensor detects a file change within 24 hours."""
    owner, repo, branch, file_path, http_conn_id = sensor_setup
    mock_github = github_mock.return_value
    mock_repo = mock_github.get_repo.return_value
    mock_branch = mock_repo.get_branch.return_value

    # Mock a commit with a file changed within the last 24 hours
    mock_commit = MagicMock()
    mock_commit.commit.author.date = datetime.now(timezone.utc) - timedelta(hours=1)
    mock_commit.files = [{'filename': file_path}]
    mock_branch.commit = mock_commit

    # Create the sensor instance
    sensor = GitHubFileChangedSensor(
        task_id='check_specific_file_changed',
        owner=owner,
        repo=repo,
        branch=branch,
        file_path=file_path,
        poke_interval=60,
        http_conn_id=http_conn_id,
        dag=test_dag,
        retry_attempts=3,
        retry_delay=5,
        timeout=10,
    )

    # Execute the poke method and assert the result
    result = sensor.poke(None)
    assert result is True, "The sensor should return True when the specified file has changed within 24 hours."

def test_file_changed_sensor_no_change(github_mock, sensor_setup):
    """Test that the GitHubFileChangedSensor returns False if no specified file has changed within 24 hours."""
    owner, repo, branch, file_path, http_conn_id = sensor_setup
    mock_github = github_mock.return_value
    mock_repo = mock_github.get_repo.return_value
    mock_branch = mock_repo.get_branch.return_value

    # Mock a commit with no file changed
    mock_commit = MagicMock()
    mock_commit.commit.author.date = datetime.now(timezone.utc) - timedelta(days=2)
    mock_commit.files = [{'filename': 'other_file.txt'}]  # Different file
    mock_branch.commit = mock_commit

    # Create the sensor instance
    sensor = GitHubFileChangedSensor(
        task_id='check_specific_file_changed',
        owner=owner,
        repo=repo,
        branch=branch,
        file_path=file_path,
        poke_interval=60,
        http_conn_id=http_conn_id,
        dag=test_dag,
        retry_attempts=3,
        retry_delay=5,
        timeout=10,
    )

    # Execute the poke method and assert the result
    result = sensor.poke(None)
    assert result is False, "The sensor should return False when no specified file has changed within 24 hours."

def test_github_exception_handling(github_mock, sensor_setup):
    """Test that the sensors handle GithubExceptions correctly by retrying."""
    owner, repo, branch, file_path, http_conn_id = sensor_setup
    mock_github = github_mock.return_value
    mock_github.get_repo.side_effect = GithubException(status=500, data='Error', headers={})

    # Create the sensor instances
    pr_sensor = GitHubPRMergedSensor(
        task_id='check_any_pr_merged',
        owner=owner,
        repo=repo,
        poke_interval=60,
        http_conn_id=http_conn_id,
        dag=test_dag,
        retry_attempts=3,
        retry_delay=1,  # Short delay for testing
        timeout=10,
    )

    file_sensor = GitHubFileChangedSensor(
        task_id='check_specific_file_changed',
        owner=owner,
        repo=repo,
        branch=branch,
        file_path=file_path,
        poke_interval=60,
        http_conn_id=http_conn_id,
        dag=test_dag,
        retry_attempts=3,
        retry_delay=1,  # Short delay for testing
        timeout=10,
    )

    # Execute the poke methods and assert the result
    pr_result = pr_sensor.poke(None)
    file_result = file_sensor.poke(None)

    assert pr_result is False, "The PR sensor should return False when an exception is raised."
    assert file_result is False, "The File sensor should return False when an exception is raised."

def test_rate_limit_exception_handling(github_mock, sensor_setup):
    """Test that the sensors handle RateLimitExceededException by retrying."""
    owner, repo, branch, file_path, http_conn_id = sensor_setup
    mock_github = github_mock.return_value
    mock_github.get_repo.side_effect = RateLimitExceededException(status=403, data='Rate limit exceeded', headers={})

    # Create the sensor instances
    pr_sensor = GitHubPRMergedSensor(
        task_id='check_any_pr_merged',
        owner=owner,
        repo=repo,
        poke_interval=60,
        http_conn_id=http_conn_id,
        dag=test_dag,
        retry_attempts=3,
        retry_delay=1,  # Short delay for testing
        timeout=10,
    )

    file_sensor = GitHubFileChangedSensor(
        task_id='check_specific_file_changed',
        owner=owner,
        repo=repo,
        branch=branch,
        file_path=file_path,
        poke_interval=60,
        http_conn_id=http_conn_id,
        dag=test_dag,
        retry_attempts=3,
        retry_delay=1,  # Short delay for testing
        timeout=10,
    )

    # Execute the poke methods and assert the result
    pr_result = pr_sensor.poke(None)
    file_result = file_sensor.poke(None)

    assert pr_result

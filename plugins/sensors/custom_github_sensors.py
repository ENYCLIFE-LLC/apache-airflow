import logging
from datetime import datetime, timedelta, timezone
from airflow.providers.github.sensors.github import GitHubSensor
from airflow.providers.github.hooks.github import GitHubHook
from github.GithubException import GithubException, RateLimitExceededException, GithubError
from time import sleep

# Initialize the logger
logger = logging.getLogger(__name__)

class GitHubPRMergedSensor(GitHubSensor):
    """
    Custom sensor to check if any pull request has been merged within the last 24 hours.
    """

    def __init__(self, owner, repo, retry_attempts=3, retry_delay=5, **kwargs):
        super().__init__(**kwargs)
        self.owner = owner
        self.repo = repo
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.last_checked_pr_number = None  # Track the last processed PR

    def poke(self, context):
        logger.info("Checking if any pull requests have been merged in %s/%s within the last 24 hours", self.owner, self.repo)
        
        attempts = 0
        while attempts < self.retry_attempts:
            try:
                hook = GitHubHook(github_conn_id=self.http_conn_id)
                github_conn = hook.get_conn()

                repo = github_conn.get_repo(f"{self.owner}/{self.repo}")

                # Fetch closed pull requests
                pulls = repo.get_pulls(state='closed', sort='updated', direction='desc')

                # Get current time and time 24 hours ago in UTC
                now = datetime.now(timezone.utc)  # Make current time timezone-aware
                yesterday = now - timedelta(days=1)

                for pr in pulls:
                    if self.last_checked_pr_number and pr.number <= self.last_checked_pr_number:
                        logger.info("Resuming from the last processed PR #%d", self.last_checked_pr_number)
                        break

                    merged_at = pr.merged_at
                    if merged_at:
                        logger.debug("Pull Request #%d: Merged at %s", pr.number, merged_at)
                        
                        # Make merged_at timezone-aware
                        merged_at_aware = merged_at.astimezone(timezone.utc)
                        
                        if merged_at_aware > yesterday:
                            logger.info("Found a merged pull request within the last 24 hours: PR #%d", pr.number)
                            self.last_checked_pr_number = pr.number  # Update the last processed PR
                            return True

                logger.info("No pull requests merged within the last 24 hours.")
                return False  # Exit loop and task

            except (RateLimitExceededException, GithubException, GithubError) as e:
                attempts += 1
                logger.error("GitHub connection error: %s. Retrying in %d seconds... (Attempt %d/%d)", str(e), self.retry_delay, attempts, self.retry_attempts)
                sleep(self.retry_delay)

        logger.error("Exceeded maximum retry attempts for connecting to GitHub.")
        return False  # Exit loop and task


class GitHubFileChangedSensor(GitHubSensor):
    """
    Custom sensor to check if a specific file has changed in the latest commit within the last 24 hours.
    """

    def __init__(self, owner, repo, branch, file_path, retry_attempts=3, retry_delay=5, **kwargs):
        super().__init__(**kwargs)
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.file_path = file_path
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.last_checked_commit_sha = None  # Track the last processed commit

    def poke(self, context):
        logger.info(
            "Checking if the file %s has changed in the latest commit on %s/%s branch %s within the last 24 hours",
            self.file_path,
            self.owner,
            self.repo,
            self.branch,
        )

        attempts = 0
        while attempts < self.retry_attempts:
            try:
                hook = GitHubHook(github_conn_id=self.http_conn_id)
                github_conn = hook.get_conn()

                repo = github_conn.get_repo(f"{self.owner}/{self.repo}")
                branch = repo.get_branch(self.branch)
                commit = branch.commit

                # Get current time and time 24 hours ago in UTC
                now = datetime.now(timezone.utc)  # Make current time timezone-aware
                yesterday = now - timedelta(days=1)

                commit_time = commit.commit.author.date
                commit_time_aware = commit_time.astimezone(timezone.utc)
                logger.debug("Latest commit SHA: %s, committed at %s", commit.sha, commit_time_aware)

                if self.last_checked_commit_sha and commit.sha == self.last_checked_commit_sha:
                    logger.info("Resuming from the last processed commit SHA: %s", self.last_checked_commit_sha)
                    return False  # No new commits to process

                if commit_time_aware > yesterday:
                    files_changed = commit.files

                    for file in files_changed:
                        logger.debug("File changed: %s", file.filename)

                    # Check if a specific file is changed
                    file_changed = any(file.filename == self.file_path for file in files_changed)
                    if file_changed:
                        logger.info("The file %s has been changed in the latest commit within the last 24 hours.", self.file_path)
                        self.last_checked_commit_sha = commit.sha  # Update the last processed commit
                        return True

                logger.info("The file %s has not changed in the latest commit within the last 24 hours.", self.file_path)
                return False  # Exit loop and task

            except (RateLimitExceededException, GithubException, GithubError) as e:
                attempts += 1
                logger.error("GitHub connection error: %s. Retrying in %d seconds... (Attempt %d/%d)", str(e), self.retry_delay, attempts, self.retry_attempts)
                sleep(self.retry_delay)

        logger.error("Exceeded maximum retry attempts for connecting to GitHub.")
        return False  # Exit loop and task

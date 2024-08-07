"""
The `GitHubSensor` does not have a `result_check` parameter. instead of, it uses the `hook` to interact with the GitHub API responses.
I implemented two custom sensors that extend the `GitHubSensor` class to check if any pull request has been merged within the last 24 hours and if a specific file has changed in the latest commit within the last 24 hours.
24 hours is the default time frame, but you can adjust it by changing the `` variable in the `poke` method.

Understanding Sensor Behavior in Airflow:
1. Poking Mechanism: Sensors are designed to keep "poking" the target at regular intervals 
until a condition is met or a timeout occurs. The poke method is called repeatedly based on the poke_interval you set.
2. Return Values: Returning True from poke signals the task is complete successfully. 
Returning False keeps the sensor poking until it times out.
3. Timeout Handling: Sensors need to handle a timeout gracefully, 
meaning that they need to exit if they have not succeeded within a given time frame.

"""
import logging
from time import sleep
from enum import Enum
from datetime import datetime, timedelta, timezone

from httpx import ReadTimeout
from airflow.providers.github.sensors.github import GithubSensor
from airflow.providers.github.hooks.github import GithubHook
from github.GithubException import GithubException, RateLimitExceededException
from airflow.exceptions import AirflowSensorTimeout


# Initialize the logger
logger = logging.getLogger(__name__)


class AllowDeltaTimeType(Enum):
    """Define an Enum for the time delta units."""
    minutes = "minutes"
    hours = "hours"
    days = "days"
    weeks = "weeks"
    
    
def return_time_delta(time_delta: int, time_unit: AllowDeltaTimeType) -> timedelta:
    """
    Return a time delta based on the time unit.
    
    :param time_delta: The time delta value.
    :param time_unit: The time unit.
    :return: A time delta.
    """
    if time_unit == AllowDeltaTimeType.minutes:
        return timedelta(minutes=time_delta)
    elif time_unit == AllowDeltaTimeType.hours:
        return timedelta(hours=time_delta)
    elif time_unit == AllowDeltaTimeType.days:
        return timedelta(days=time_delta)
    elif time_unit == AllowDeltaTimeType.weeks:
        return timedelta(weeks=time_delta)
    else:
        raise ValueError("Invalid time unit. Please choose from minutes, hours, days, or weeks.")
    
    
class GitHubPRMergedSensor(GithubSensor):
    """
    Custom sensor to check if any pull request has been merged within delta_time.
    """

    def __init__(
        self, 
        github_conn_id: str, 
        owner:str, 
        repo:str, 
        branch: str,
        delta_time: int = 24, # 24 hours as default delta time
        delta_time_type=AllowDeltaTimeType.hours,
        retry_attempts=3, 
        retry_delay=5, 
        **kwargs
    ):
        super().__init__(method_name="get_pull", **kwargs)
        self.github_conn_id = github_conn_id
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.delta_time = delta_time
        self.delta_time_type = delta_time_type
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.last_checked_pr_number = None  # Track the last processed PR number

    def poke(self, context):
        logger.info("Checking if any pull requests have been merged in %s/%s within given delta_time", self.owner, self.repo)
        
        attempts = 0
        while attempts < self.retry_attempts:
            try:
                hook = GithubHook(github_conn_id=self.github_conn_id)
                github_conn = hook.get_conn()

                repo = github_conn.get_repo(f"{self.owner}/{self.repo}")

                # Fetch closed pull requests sort by update time in descending order
                pulls = repo.get_pulls(state='closed', sort='updated', base=self.branch, direction='desc')

                # Get current time and time 24 hours ago in UTC
                curr_dt = datetime.now(timezone.utc)  # Make current time timezone-aware
                logging.info("current datetime: %s", curr_dt.strftime("%Y-%m-%d %H:%M:%S"))
                past_pr_dt = curr_dt - return_time_delta(self.delta_time, self.delta_time_type)
                logging.info("Checkpoint of the Pasted PR Merged datetime datetime: %s", past_pr_dt.strftime("%Y-%m-%d %H:%M:%S"))
                
                for pr in pulls:
                    if self.last_checked_pr_number and pr.number <= self.last_checked_pr_number:
                        logger.info("Resuming from the last processed PR #%d", self.last_checked_pr_number)
                        break 

                    merged_at = pr.merged_at
                    if merged_at:
                        logger.debug("Pull Request #%d: Merged at %s", pr.number, merged_at)
                        
                        # Make merged_at timezone-aware
                        merged_at_aware = merged_at.astimezone(timezone.utc)
                        logging.info("The PR Merged datetime datetime: %s", merged_at_aware.strftime("%Y-%m-%d %H:%M:%S"))
                        if merged_at_aware > past_pr_dt:
                            logger.info("Found a merged pull request within the last 24 hours: PR #%d", pr.number)
                            self.last_checked_pr_number = pr.number  # Update the last processed PR
                            return True
                else:
                    logger.info("No Closed pull requests merged from the search")

                logger.info("No pull requests merged within the last %d %s.", self.delta_time, self.delta_time_type)
                return False  # Exit loop and task

            except (RateLimitExceededException, GithubException, ReadTimeout, AirflowSensorTimeout) as e:
                logger.error("Exception or Timeout: %s.", str(e))
                attempts += 1
                if attempts < self.retry_attempts:
                    logger.info("Retrying in %d seconds... (Attempt %d/%d)", self.retry_delay, attempts, self.retry_attempts)
                    sleep(self.retry_delay)
                else:
                    logger.error("Exceeded maximum retry attempts for connecting to GitHub.")
                    return False
                

        logger.error("Exceeded maximum retry attempts for connecting to GitHub.")
        return False  # Exit loop and task


class GitHubFileChangedSensor(GithubSensor):
    """
    Custom sensor to check if a specific file has changed in the latest commit within the last 24 hours.
    """

    def __init__(
        self, 
        github_conn_id: str,
        owner:str, 
        repo:str, 
        branch:str, 
        file_path:str, 
        delta_time: int = 24, # 24 hours as default delta time
        delta_time_type=AllowDeltaTimeType.hours,
        retry_attempts=3, 
        retry_delay=5, 
        **kwargs
    ):
        super().__init__(method_name="get_commit", **kwargs)
        self.github_conn_id = github_conn_id
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.file_path = file_path
        self.delta_time = delta_time
        self.delta_time_type = delta_time_type
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.checked_commits_sha_list = []  # Track the last processed commit

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
                # Establish a connection to the GitHub using the token
                hook = GithubHook(github_conn_id=self.github_conn_id)
                github_conn = hook.get_conn()

                repo = github_conn.get_repo(f"{self.owner}/{self.repo}")

                # Get current time and time 24 hours ago in UTC
                curr_dt = datetime.now(timezone.utc)  # Make current time timezone-aware
                logging.info("current datetime: %s", curr_dt.strftime("%Y-%m-%d %H:%M:%S"))
                past_commit_dt = curr_dt - return_time_delta(self.delta_time, self.delta_time_type)
                logging.info("past_commit_dt datetime: %s", past_commit_dt.strftime("%Y-%m-%d %H:%M:%S"))

                # Retrieve the list of commits on the branch since the specified time
                # sha parameter is the commit SHA or branch name
                commits = repo.get_commits(since=past_commit_dt, sha=self.branch)
                logger.info("Total commits since %s: %d", past_commit_dt, commits.totalCount)
                
                for c in commits:
                    logger.info("Commit SHA: %s, %s", c.sha, c.commit.author.date)
                for commit in commits:
                    if commit.sha in self.checked_commits_sha_list:
                        logger.info("Skipped checked commit sha: %s", commit.sha)
                        continue
                    # Get the commit time
                    commit_time = commit.commit.author.date
                    commit_time_aware = commit_time.astimezone(timezone.utc)
                    logger.info("Latest commit SHA: %s, committed at %s", commit.sha, commit_time_aware)

                    if commit_time_aware > past_commit_dt:
                        logger.info(
                            "Checking... if the file %s has been changed in the latest commit on %s/%s branch %s.", 
                            self.file_path,
                            self.owner,
                            self.repo,
                            self.branch
                        )
                        files_changed = commit.files
                        for _f in files_changed:
                            logger.info("Changed file: %s", _f.filename)
                        # Check if a specific file is changed
                        file_changed = any(file.filename.lower() == (self.file_path).lower() for file in files_changed)
                        if file_changed:
                            logger.info("The file %s has been changed in the latest commit.", self.file_path)
                            return True
                        else:
                            self.checked_commits_sha_list.append(commit.sha) 
                            logger.info("Added the checked and not incldue the file %s commit sha to skip list: %s", self.file_path, commit.sha)
                    else:
                        # the commit date is out of the time frame
                        self.checked_commits_sha_list.append(commit.sha) 
                        logger.info("Added the checked and out scoped commit sha to skip list: %s", commit.sha)

                logger.info("The file %s has NOT changed in the latest commit within the last 24 hours.", self.file_path)
                return False  # Exit loop and task

            except (RateLimitExceededException, GithubException, ReadTimeout, AirflowSensorTimeout) as e:
                logger.error("Exception or Timeout: %s.", str(e))
                attempts += 1
                if attempts < self.retry_attempts:
                    logger.info("Retrying in %d seconds... (Attempt %d/%d)", self.retry_delay, attempts, self.retry_attempts)
                    sleep(self.retry_delay)
                else:
                    logger.error("Exceeded maximum retry attempts for connecting to GitHub.")
                    return False

        logger.error("Exceeded maximum retry attempts for connecting to GitHub.")
        return False  # Exit loop and task

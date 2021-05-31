import subprocess
import re

from typing import Optional
from typing_extensions import Literal

BranchType = Literal["feature", "bugfix"]
CompletedProcess = subprocess.CompletedProcess

class GitAPI():

    # Matches Moneyfarm branch structure (i.e. feature/COR-1-blabla-bla)
    branch_rgx = re.compile(r"\w+/(\w{1,6}-\d{1,4})-(.*)")

    def create_branch(self, branchType: BranchType, issueKey: str, issueSummary: str) -> CompletedProcess:
        summary_param_case = issueSummary.lower().replace(' ', '-')
        branch_name = f"{branchType}/{issueKey}-{summary_param_case}"
        command_string = f"git checkout -b {branch_name}"
        command = command_string.split(" ")

        return subprocess.run(command, capture_output=True)

    def commit_changes(self, message: str) -> CompletedProcess:
        current_branch: str = self.get_current_branch()
        maybe_commit_prefix: Optional[str] = self.__get_issue_key_from_branch(current_branch)

        lowered_message = self.__lower_first_letter(message)

        if maybe_commit_prefix:
            commit_message = f"{maybe_commit_prefix}: {lowered_message}"
        else:
            commit_message = f"{message}"

        command_string = "git commit -m"
        command = command_string.split(" ")
        command.append(commit_message)

        return subprocess.run(command, capture_output=True)


    def push_changes(self, branchName: str) -> CompletedProcess:
        command_string = f"git push --set-upstream origin {branchName}"
        command = command_string.split(" ")

        return subprocess.run(command, capture_output=True)

    def get_current_branch(self) -> str:
        command_string = "git rev-parse --abbrev-ref HEAD"
        command = command_string.split(" ")

        result = subprocess.run(command, capture_output=True)
        return str(result.stdout, 'utf-8').strip()

    def get_pretty_current_branch(self) -> str:
        current_branch = self.get_current_branch()
        maybe_issue_key: Optional[str] = self.__get_issue_key_from_branch(current_branch)
        maybe_issue_title: Optional[str] = self.__get_issue_title_from_branch(current_branch)

        if maybe_issue_key and maybe_issue_title:
            title = maybe_issue_title.replace("-", " ")
            return f"{maybe_issue_key}: {title}"

        return current_branch


    def __get_issue_key_from_branch(self, branch: str) -> Optional[str]:
        match = self.branch_rgx.match(branch)
        if (match):
            return match.group(1)
        return None

    def __get_issue_title_from_branch(self, branch: str) -> Optional[str]:
        match = self.branch_rgx.match(branch)
        if (match):
            return match.group(2)
        return None

    def __lower_first_letter(self, message: str) -> str:
       return message[0].lower() + message[1:]

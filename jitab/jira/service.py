import questionary # type: ignore

from typing import List, Set, Dict, Optional, Any

from jitab.jira.api import JiraAPI

from jitab.jira.model import Issue, AccountId

class JiraService():

    def __init__(self, jiraApi: JiraAPI):
        self.jiraApi = jiraApi
    
    def init_work(self, flowType: str, projectKeys: List[str], statuses: List[str], currentUser: Optional[str] = None) -> Optional[Issue]:
        selected_issue: Optional[Issue] = self.__ask_for_issue(flowType, projectKeys, statuses)

        if (selected_issue and not currentUser):
            account_id: AccountId = self.jiraApi.get_account_id()
            result: bool = self.jiraApi.assign_issue_to_current_user(selected_issue.key, account_id.id)

            if not result:
                print(f"There was an issue assigning current user (account id: {account_id.id}) to the selected issue ({selected_issue.key})")

        return selected_issue

    
    def __ask_for_issue(self, flowType: str, projectKeys: List[str], statuses: List[str], currentUser: Optional[str] = None) -> Optional[Issue]:
        issues: List[Issue] = self.jiraApi.get_issues(flowType, projectKeys, statuses, currentUser)
        issue_descriptions = list(map(lambda i: i.summary, issues))

        if (len(issues) == 0):
            return None

        if (len(issues) == 1):
            return issues[0]

        answer = questionary.select(
            "Which ticket do you want to work on?",
            choices = issue_descriptions
        ).ask()

        if answer:
            return list(filter(lambda i: i.summary == answer, issues))[0]
        
        return None
    
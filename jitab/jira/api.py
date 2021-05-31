import requests
import json

from requests.auth import HTTPBasicAuth
from typing import List, Set, Dict, Optional, Any

from jitab.jira.model import Issue, Board, Project, AccountId

Response = requests.models.Response

class JiraAPI():

    def __init__(self, username: str, token: str):
        self.username = username
        self.token = token

    def get_board_statuses(self, projectKey: str) -> Set[str]:
        url = f"https://<redacted>/rest/api/3/project/{projectKey}/statuses"
        status_set: Set[str] = set()
        http_resp: Response = self.__make_get_request(url)

        for issueType in http_resp.json():
            for status in issueType["statuses"]:
                status_set.add(status["name"])

        return status_set
    
    def get_boards_info(self) -> List[Board]:
        url = "https://<redacted>/rest/agile/1.0/board"
        http_resp: Response = self.__make_get_request(url)
        board_list: List[Board] = []

        for board in http_resp.json()["values"]:
            try:
                board_list.append(Board(board["id"], board["name"], board["location"]["projectKey"], board["location"]["projectName"], board["type"]))
            except KeyError:
                pass
        
        return board_list

    def get_board_columns(self, boardId: str) -> List[str]:
        url = f"https://<redacted>/rest/agile/1.0/board/{boardId}/configuration"
        http_resp: Response = self.__make_get_request(url)

        return [column["name"] for column in http_resp.json()["columnConfig"]["columns"]]

    def get_issues(self, flowType: str, projectKeys: List[str], statuses: List[str], currentUser: Optional[str] = None) -> List[Issue]:
        issue_list: List[Issue] = []

        project_string = self.__build_search_string_by_term("project", projectKeys)
        statuses_string = self.__build_search_string_by_term("status", statuses)
        search_string = f'({project_string}) AND ({statuses_string}) AND type != Epic'
        if flowType == "kanban" or flowType == "simple":
            search_string += f' ORDER BY Rank ASC'
        elif flowType == "scrum":
            search_string += f' AND sprint in openSprints()'
        else:
            # Log the problem -> flow not supported
            return []
        
        if currentUser:
            search_string += f' AND assignee=currentUser()'
        
        http_resp: Response = self.__make_get_request(f'https://<redacted>/rest/api/3/search?jql={search_string}&fields=summary,assignee&maxResults=100')

        for issue in http_resp.json()["issues"]:
            id: str = issue["id"]
            key: str = issue["key"]
            summary: str = issue["fields"]["summary"]
            assignee: Optional[str] = None
            if issue["fields"]["assignee"] is not None:
                assignee = issue["fields"]["assignee"]["accountId"]
            issue_list.append(Issue(id, key, summary, assignee))

        return issue_list

    def get_account_id(self) -> AccountId:
        http_resp: Response = self.__make_get_request(f'https://<redacted>/rest/api/3/user/bulk/migration?username={self.username}')

        accountId = AccountId(http_resp.json()[0]["accountId"])

        return accountId

    def get_loggedin_username(self) -> str:
        http_resp: Response = self.__make_get_request(f'https://<redacted>/rest/auth/latest/session')

        return http_resp.json()["name"]

    def assign_issue_to_current_user(self, issueKey: str, accountId: str) -> bool:
        url = f'https://<redacted>/rest/api/3/issue/{issueKey}/assignee'
        payload = json.dumps({
          "accountId": f'{accountId}'
        })

        http_resp = self.__make_put_request(url, payload)

        return http_resp.ok

    def __make_get_request(self, url: str) -> Response:
        headers = {
            "Authorization": f'Basic {self.token}',
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        return requests.get(url, headers = headers)

    def __make_put_request(self, url: str, payload: str) -> Response:
        headers = {
            "Authorization": f'Basic {self.token}',
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        return requests.put(url, data = payload, headers = headers)

    def __make_post_request(self, url: str, payload: str) -> Response:
        headers = {
            "Authorization": f'Basic {self.token}',
            "Accept": "application/json",   
            "Content-Type": "application/json"
        }

        return requests.post(url, data = payload, headers = headers)

    def __build_search_string_by_term(self, searchTerm: str, fieldValues: List[str]) -> str:
        last_element: str = fieldValues[-1]
        search_string = ""
        for element in fieldValues:
            if element == last_element:
                search_string += f'{searchTerm} = "{element}"'
            else:
                search_string += f'{searchTerm} = "{element}" OR '
        
        return search_string

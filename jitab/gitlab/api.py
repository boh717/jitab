import requests
import json

from jitab.gitlab.model import Repository, MergeRequestResponse
from typing import List

Response = requests.models.Response

class GitlabAPI():

    def __init__(self, username: str, token: str):
        self.username = username
        self.token = token

    def search_project(self, project: str) -> List[Repository]:
        url = f"https://gitlab.com/api/v4/projects?search={project}&order_by=last_activity_at"
        http_resp: Response = self.__make_get_request(url)

        return [Repository(repo["id"], repo["name"], repo["description"], repo["path"]) for repo in http_resp.json()]

    def create_merge_request(self, projectId: str, source_branch: str, target_branch: str, title: str) -> MergeRequestResponse:
        url = f"https://gitlab.com/api/v4/projects/{projectId}/merge_requests"
        payload = json.dumps({
          "id": f'{projectId}',
          "source_branch": f'{source_branch}',
          "target_branch": f'{target_branch}',
          "title": f'{title}',
          "remove_source_branch": True,
          "squash": True
        })

        http_resp = self.__make_post_request(url, payload)

        return MergeRequestResponse(http_resp.status_code, http_resp.reason, http_resp.json()["web_url"])

    def __make_get_request(self, url: str) -> Response:
        headers = {
            "PRIVATE-TOKEN": f'{self.token}',
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        return requests.get(url, headers = headers)

    def __make_put_request(self, url: str, payload: str) -> Response:
        headers = {
            "PRIVATE-TOKEN": f'{self.token}',
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        return requests.put(url, data = payload, headers = headers)

    def __make_post_request(self, url: str, payload: str) -> Response:
        headers = {
            "PRIVATE-TOKEN": f'{self.token}',
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        return requests.post(url, data = payload, headers = headers)

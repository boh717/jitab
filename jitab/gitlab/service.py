import questionary # type: ignore

from typing import Optional

from jitab.gitlab.api import GitlabAPI

from jitab.gitlab.model import Repository

class RepoInitService():

    def __init__(self, gitlabApi: GitlabAPI):
        self.gitlabApi = gitlabApi
    
    def run_init(self, projectName: str) -> Optional[Repository]:

        return self.__ask_for_repository(projectName)

    
    def __ask_for_repository(self, project_names: str) -> Optional[Repository]:
        repositories = self.gitlabApi.search_project(project_names)
        repo_names = list(map(lambda i: i.name, repositories))

        if (len(repositories) == 0):
            return None

        if (len(repositories) == 1):
            return repositories[0]

        answer = questionary.select(
            "Which repository are you initializing?",
            choices = repo_names
        ).ask()

        if answer:
            return list(filter(lambda i: i.name == answer, repositories))[0]
        
        return None
    
import questionary # type: ignore

from typing import Optional

from jitab.jira.api import JiraAPI

from jitab.jira.model import Board
from jitab.config.model import ColumnAnswer, Configuration

class ConfigService():

    def __init__(self, jiraApi: JiraAPI):
        self.jiraApi = jiraApi
    
    def run_config(self) -> Optional[Configuration]:
        board = self.__ask_for_board()

        if (board):
            columns = self.__ask_for_columns(board.id)
        
        if (board and columns):
            return Configuration(board, columns)

        return None
    
    def __ask_for_board(self) -> Optional[Board]:
        jira_boards = self.jiraApi.get_boards_info()
        board_names = list(map(lambda i: i.name, jira_boards))
        board_names.sort()

        answer = questionary.select(
            "Which board do you want to track?",
            choices = board_names
        ).ask()

        if (answer):
            chosen_project = list(filter(lambda i: i.name == answer, jira_boards))[0]
            return chosen_project
        
        return None
    
    def __ask_for_columns(self, boardId: str) -> Optional[ColumnAnswer]:
        columns = self.jiraApi.get_board_columns(boardId)

        new_columns = questionary.checkbox(
            'Which columns do you usually pick new stories from?',
            choices= columns
        ).ask()

        wip_columns = questionary.checkbox(
            'Which columns do you usually pick already-started stories from?',
            choices= columns
        ).ask()

        if (new_columns and wip_columns):
            return ColumnAnswer(all_columns = columns, new_columns = new_columns, wip_columns = wip_columns)
        
        return None
from dataclasses import dataclass

from typing import Optional, List

from jitab.jira.model import Board

@dataclass
class ColumnAnswer:
    all_columns: List[str]
    new_columns: List[str]
    wip_columns: List[str]

@dataclass
class Configuration:
    board: Board
    columns: ColumnAnswer
from dataclasses import dataclass

from typing import Optional, List

@dataclass
class Issue:
    id: str
    key: str
    summary: str
    assignee: Optional[str]

@dataclass
class Board:
    id: str
    name: str
    projectKey: str
    projectName: str
    flow_type: str

@dataclass
class Project:
    id: str
    name: str
    key: str

@dataclass
class AccountId:
    id: str

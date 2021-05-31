from dataclasses import dataclass

from typing import Optional

@dataclass
class Repository:
    id: str
    name: str
    description: Optional[str]
    path: str

@dataclass
class MergeRequestResponse:
    status_code: int
    message: str
    link: str
from dataclasses import dataclass
from datetime import date


@dataclass
class Absence:
    subject: str
    date: date
    is_motivated: bool


@dataclass
class Grade:
    subject: str
    date: date
    grade: int

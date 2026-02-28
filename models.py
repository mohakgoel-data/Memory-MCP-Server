from pydantic import BaseModel, field_validator
from typing import List
from enum import Enum



class Category(str, Enum):
    identity="identity",
    preference="preference",
    goal="goal",
    project="project",
    skill="skill",
    constraint="constraint",
    instruction="instruction",
    fact="fact"

class MemoryEntry(BaseModel):
    category: Category
    tag: str
    content: str
    importance: int

    @field_validator('importance')
    @classmethod
    def clamp_importance(cls, v):
        return max(1, min(3, v))

class ExtractionResult(BaseModel):
    memories: List[MemoryEntry]
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ContactLink(BaseModel):
    id: str
    label: str
    url: str


class HeaderContent(BaseModel):
    name: str = ""
    title: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    website: str = ""
    links: List[ContactLink] = Field(default_factory=list)


class BulletItem(BaseModel):
    id: str
    text: str


class SectionItem(BaseModel):
    id: str
    title: str = ""
    subtitle: str = ""
    location: str = ""
    dateRange: str = ""
    bullets: List[BulletItem] = Field(default_factory=list)


SectionType = Literal[
    "summary",
    "experience",
    "skills",
    "education",
    "projects",
    "certifications",
    "custom",
]


class ResumeSection(BaseModel):
    id: str
    type: SectionType
    title: str
    visible: bool = True
    items: List[SectionItem] = Field(default_factory=list)


class ResumeContent(BaseModel):
    header: HeaderContent = Field(default_factory=HeaderContent)
    sections: List[ResumeSection] = Field(default_factory=list)

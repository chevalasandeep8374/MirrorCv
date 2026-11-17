from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ContactLink(BaseModel):
    id: str
    label: str
    url: str


SectionType = Literal[
    "summary",
    "experience",
    "skills",
    "education",
    "projects",
    "certifications",
    "custom",
    "languages",
    "awards",
    "publications",
    "volunteering",
    "interests",
    "references",
    "links",
]


class HeaderContent(BaseModel):
    name: str = ""
    title: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    website: str = ""
    photoUrl: Optional[str] = None
    fieldVisibility: Optional[dict] = None
    links: List[ContactLink] = Field(default_factory=list)


class BulletItem(BaseModel):
    id: str
    text: str
    level: Optional[int] = 0


class SectionItem(BaseModel):
    id: str
    title: str = ""
    subtitle: str = ""
    location: str = ""
    dateRange: str = ""
    visible: bool = True
    itemType: Optional[Literal["list", "paragraph", "timeline", "tags"]] = None
    bullets: List[BulletItem] = Field(default_factory=list)


class ResumeSection(BaseModel):
    id: str
    type: SectionType
    title: str
    visible: bool = True
    pageBreakBefore: Optional[bool] = False
    items: List[SectionItem] = Field(default_factory=list)


class RecipientContent(BaseModel):
    name: str = ""
    title: str = ""
    company: str = ""
    address: str = ""
    email: str = ""


class CoverLetterParagraph(BaseModel):
    id: str
    text: str


class CoverLetterContent(BaseModel):
    sender: HeaderContent = Field(default_factory=HeaderContent)
    recipient: RecipientContent = Field(default_factory=RecipientContent)
    date: str = ""
    salutation: str = ""
    paragraphs: List[CoverLetterParagraph] = Field(default_factory=list)
    closing: str = ""
    signature: str = ""


class ResumeContent(BaseModel):
    header: HeaderContent = Field(default_factory=HeaderContent)
    sections: List[ResumeSection] = Field(default_factory=list)
    coverLetter: Optional[CoverLetterContent] = None

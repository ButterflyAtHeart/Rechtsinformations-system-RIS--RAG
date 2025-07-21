from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase):
    pass
class Document(Base):
    __tablename__ = "document"
    uri: Mapped[str] = mapped_column(Text, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    short_title: Mapped[str] = mapped_column(Text)
    abbreviation: Mapped[str] = mapped_column(Text)
    date: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(Text)
    preamble: Mapped[Optional[str]] = mapped_column(Text)
    articles: Mapped[List["Article"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    embedding = mapped_column(Vector(1024))
    def __repr__(self) -> str:
        return f"{self.title}"


class Article(Base):
    __tablename__ = "article"
    document_uri: Mapped[str] = mapped_column(ForeignKey("document.uri"))
    guid: Mapped[str] = mapped_column(Text, primary_key=True)
    number: Mapped[str] = mapped_column(Text, nullable=True)
    heading: Mapped[Optional[str]] = mapped_column(Text)
    paragraphs: Mapped[List["Paragraph"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )
    document: Mapped["Document"] = relationship(back_populates="articles")
    embedding = mapped_column(Vector(1024))

    def __repr__(self) -> str:
        return f"**{self.number} {self.heading}**\n{"\n".join([str(p) for p in self.paragraphs])}"

class Paragraph(Base):
    __tablename__ = "paragraph"
    guid: Mapped[int] = mapped_column(Text, primary_key=True)
    article_guid: Mapped[int] = mapped_column(ForeignKey("article.guid"))
    number: Mapped[str] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text)
    article: Mapped["Article"] = relationship(back_populates="paragraphs")

    def __repr__(self) -> str:
        if self.number:
            return f"{self.number} {self.content}"
        else:
            return f"{self.content}"